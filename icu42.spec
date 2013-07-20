%define packagename icu

# Force include and library files into a nonstandard place
%{expand: %%define _origincludedir %{_includedir}}
%{expand: %%define _origlibdir %{_libdir}}
%define _includedir %{_origincludedir}/%{name}
%define _libdir %{_origlibdir}/%{name}

Name:      icu42
Version:   4.2.1
Release:   2%{?dist}
Summary:   International Components for Unicode
Group:     Development/Tools
License:   MIT and UCD and Public Domain
URL:       http://www.icu-project.org/
Source0:   http://download.icu-project.org/files/icu4c/4.2.1/icu4c-4_2_1-src.tgz
Source1:   icu-config
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: doxygen, autoconf
Requires: lib%{name} = %{version}-%{release}
Provides: icu = %{version}-%{release}
Conflicts: icu < %{version}

Patch1:  icu-3.4-multiarchdevel.patch
Patch2:  icu.6995.kannada.patch
Patch3:  icu.icu7039.badextract.patch
Patch4:  icu.6969.pkgdata.patch
Patch5:  icu.XXXX.install.patch
Patch6:  icu.7119.s390x.patch
Patch7:  canonicalize.patch

%description
Tools and utilities for developing with icu.

%package -n lib%{name}
Summary: International Components for Unicode - libraries
Group:   System Environment/Libraries

%description -n lib%{name}
The International Components for Unicode (ICU) libraries provide
robust and full-featured Unicode services on a wide variety of
platforms. ICU supports the most current version of the Unicode
standard, and they provide support for supplementary Unicode
characters (needed for GB 18030 repertoire support).
As computing environments become more heterogeneous, software
portability becomes more important. ICU lets you produce the same
results across all the various platforms you support, without
sacrificing performance. It offers great flexibility to extend and
customize the supplied services.

%package  -n lib%{name}-devel
Summary:  Development files for International Components for Unicode
Group:    Development/Libraries
Requires: lib%{name} = %{version}-%{release}
Requires: pkgconfig

%description -n lib%{name}-devel
Includes and definitions for developing with icu.

%package -n lib%{name}-doc
Summary: Documentation for International Components for Unicode
Group:   Documentation
Provides: libicu-doc = %{version}-%{release}
Conflicts: libicu-doc < %{version}

%description -n lib%{name}-doc
%{summary}.

%prep
%setup -q -n %{packagename}
%patch1 -p1 -b .multiarchdevel
%patch2 -p1 -b .icu6995.kannada.patch
%patch3 -p1 -b .icu7039.badextract.patch
%patch4 -p0 -b .icu.6969.pkgdata.patch
%patch5 -p1 -b .icu.XXXX.install.patch
%patch6 -p1 -b .icu.7119.s390x.patch
%patch7 -p0 -b .canonicalize.patch

%build
cd source
sed -e '/AC_PREREQ/s/2.63/2.59/' -i configure.in
autoconf
CFLAGS='%optflags -fno-strict-aliasing'
CXXFLAGS='%optflags -fno-strict-aliasing'
%configure --with-data-packaging=library --disable-samples
#rhbz#225896
sed -i -- "s/-nodefaultlibs -nostdlib//" config/mh-linux
make # %{?_smp_mflags} # -j(X>1) may "break" man pages as of 3.2, b.f.u #2357
make doc

%install
rm -rf $RPM_BUILD_ROOT source/__docs
make -C source install DESTDIR=$RPM_BUILD_ROOT
make -C source install-doc docdir=__docs
chmod +x $RPM_BUILD_ROOT%{_libdir}/*.so.*
cp -p %{SOURCE1} $RPM_BUILD_ROOT%{_bindir}/%{name}-icu-config
chmod 0755 $RPM_BUILD_ROOT%{_bindir}/%{name}-icu-config
rm $RPM_BUILD_ROOT%{_bindir}/icu-config

mv $RPM_BUILD_ROOT%{_mandir}/man1/icu-config.1.gz $RPM_BUILD_ROOT%{_mandir}/man1/icu42-icu-config.1.gz

mkdir -p ${RPM_BUILD_ROOT}%{_origlibdir}
pushd ${RPM_BUILD_ROOT}%{_origlibdir}
mv -f ${RPM_BUILD_ROOT}%{_libdir}/libicu*.so.42.* .
cp -p -d ${RPM_BUILD_ROOT}%{_libdir}/libicu*.so.42 .
popd

pushd ${RPM_BUILD_ROOT}%{_libdir}
find ../.. -name 'libicu*.so.42.*' -print0 | xargs -0 -I {} ln -s {} .
popd

sed -i s/\\\$\(THREADSCXXFLAGS\)// $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/icu.pc
sed -i s/\\\$\(THREADSCPPFLAGS\)/-D_REENTRANT/ $RPM_BUILD_ROOT/%{_libdir}/pkgconfig/icu.pc

mv $RPM_BUILD_ROOT/%{_libdir}/pkgconfig $RPM_BUILD_ROOT/%{_origlibdir}/pkgconfig
mv $RPM_BUILD_ROOT/%{_origlibdir}/pkgconfig/icu.pc $RPM_BUILD_ROOT/%{_origlibdir}/pkgconfig/icu42.pc

%check
make -C source check

%clean
rm -rf $RPM_BUILD_ROOT

%post -n lib%{name} -p /sbin/ldconfig

%postun -n lib%{name} -p /sbin/ldconfig

%files
%defattr(-,root,root,-)
%doc license.html readme.html
%{_bindir}/derb
%{_bindir}/genbrk
%{_bindir}/gencfu
%{_bindir}/gencnval
%{_bindir}/genctd
%{_bindir}/genrb
%{_bindir}/makeconv
%{_bindir}/pkgdata
%{_bindir}/uconv
%{_sbindir}/*
%{_mandir}/man1/derb.1*
%{_mandir}/man1/gencnval.1*
%{_mandir}/man1/genrb.1*
%{_mandir}/man1/genbrk.1*
%{_mandir}/man1/genctd.1*
%{_mandir}/man1/makeconv.1*
%{_mandir}/man1/pkgdata.1*
%{_mandir}/man1/uconv.1*
%{_mandir}/man8/*.8*

%files -n lib%{name}
%defattr(-,root,root,-)
%{_origlibdir}/*.so.*

%files -n lib%{name}-devel
%defattr(-,root,root,-)
%{_bindir}/%{name}-icu-config
%{_mandir}/man1/%{name}-icu-config.1*
%{_includedir}/layout
%{_includedir}/unicode
%{_libdir}/*.so
%{_libdir}/*.so.*
%{_origlibdir}/pkgconfig/icu42.pc
%{_libdir}/%{packagename}
%dir %{_datadir}/%{packagename}
%dir %{_datadir}/%{packagename}/%{version}
%{_datadir}/%{packagename}/%{version}/install-sh
%{_datadir}/%{packagename}/%{version}/mkinstalldirs
%{_datadir}/%{packagename}/%{version}/config
%doc %{_datadir}/%{packagename}/%{version}/license.html

%files -n lib%{name}-doc
%defattr(-,root,root,-)
%doc source/__docs/%{packagename}/html/*

%changelog
* Sat Jul 20 2013 Andy Thompson <andy@webtatic.com> - 4.2.1-2
- Change libicu42 to be installable in parallel with libicu and relax conflicts

* Sat Jun 22 2013 Andy Thompson <andy@webtatic.com> - 4.2.1-1
- Fork from EL 6.4 icu-4.2.1-9.1
- Update package name to icu42
- Add conflicts for packages against icu/libicu
