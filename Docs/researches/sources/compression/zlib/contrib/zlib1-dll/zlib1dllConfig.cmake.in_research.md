# sources/compression/zlib/contrib/zlib1-dll/zlib1dllConfig.cmake.in

Purpose: Installed package configuration template for the zlib1-dll CMake package.

Important APIs, types, and functions: Uses `@PACKAGE_INIT@`, optionally includes adjacent `ZLIB1DLLTargets.cmake`, and calls `check_required_components(ZLIB1-DLL)`.

Control flow: At package discovery time, CMake package initialization runs, targets are imported if the target file exists, and component requirements are checked.

State and persistence: Mutates the caller's package-discovery variables and imports targets into the caller's CMake target graph.

Dependencies and integration points: Generated and installed by `contrib/zlib1-dll/CMakeLists.txt`; consumed by the find-package test template and downstream projects.

Risks: The include is `OPTIONAL`, so missing target files may not fail until target use or component checks. The component name passed to `check_required_components` uses `ZLIB1-DLL`, while consumers call `find_package(ZLIB1DLL)`, which may be inconsistent with conventional package variable names.

Test signals: `zlib1-dll/test/find_package_test.cmake.in` validates that imported targets are actually available after package discovery.
