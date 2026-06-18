<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/pack.cmake -->
# sources/cloud-native/overlaybd/CMake/pack.cmake

Purpose: Defines CPack metadata for RPM and DEB packages.

APIs and control flow: Sets package version, name, release, contact/vendor, install prefix, filename pattern, RPM license/summary/description, and Debian version/shlibdeps before including `CPack`.

State and persistence: Generates RPM/DEB package files during `cpack`.

Dependencies and integration: Release script passes `PACKAGE_VERSION` and `PACKAGE_RELEASE`; installation rules in CMakeLists supply daemon binary, service unit, configs, base layer, and bundled ext2fs libs.

Risks and test signals: `CPACK_DEBIAN_PACKAGE_SHLIBDEPS` depends on distro tooling. Package file naming and release assets validate the path.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/CMake/pack.cmake -->
