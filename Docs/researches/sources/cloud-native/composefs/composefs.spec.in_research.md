# sources/cloud-native/composefs/composefs.spec.in

Purpose: RPM spec template for packaging composefs tools, library, and development files.

Important APIs/types/functions: package metadata, `%bcond man`, `BuildRequires`, runtime `Requires`, subpackages `devel` and `libs`, `%meson` configure with FUSE/man options, `%meson_build`, `%meson_install`, static library removal, and `%files` lists.

Control flow: RPM build expands `@VERSION@`, downloads source tarball, sets up sources, builds shared library/tools, installs, splits files into packages, and generates changelog via `%autochangelog`.

State/persistence: installed RPM package contents and dependency metadata.

Dependencies/integration: Fedora/RPM ecosystem, Meson macros, OpenSSL, fuse3, go-md2man on Go arches, and composefs release tarballs.

Risks/test signals: package file lists must track installed outputs; license expressions must match source. CI build does not necessarily exercise RPM build, so distro packaging is a separate validation lane.
