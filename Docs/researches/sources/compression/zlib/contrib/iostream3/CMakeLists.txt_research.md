# sources/compression/zlib/contrib/iostream3/CMakeLists.txt

Purpose: builds, installs, packages, and tests the modernized iostream3 gzip C++ stream wrapper.

Important APIs/types/functions: project `iostreamV3`, options `ZLIB_IOSTREAM3_BUILD_SHARED`, `ZLIB_IOSTREAM3_BUILD_STATIC`, `ZLIB_IOSTREAM3_BUILD_TESTING`, and `ZLIB_IOSTREAM3_INSTALL`; targets `iostream3_iostreamv3`, `iostream3_iostreamv3Static`; aliases `IOSTREAMV3::IOSTREAMV3` and `IOSTREAMV3::IOSTREAMV3STATIC`; generated package config/version files.

Control flow: when built from zlib, options inherit parent values. Standalone builds find required ZLIB components. Shared and static libraries are conditionally declared from `zfstream.cc`/`.h`, linked to corresponding zlib imported targets, assigned export/output names, and optionally installed with export files. Testing adds the `test/` subdirectory.

State and persistence: mutates CMake build/install state and writes generated config files in the binary tree.

Dependencies/integration: depends on CMake 3.12 to 3.31, `GNUInstallDirs`, `CMakePackageConfigHelpers`, and ZLIB config packages.

Risks: option help text incorrectly says "blast" in several places. `write_basic_package_version_file()` uses `${iostream3_VERSION}`, while the project variable is expected as `iostreamV3_VERSION`, which can produce an empty version if not defined elsewhere. Shared install lacks explicit LIBRARY destination.

Test signals: `test/CMakeLists.txt` builds shared/static executables and package-consumption configure tests.
