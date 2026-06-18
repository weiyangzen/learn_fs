# sources/compression/zlib/test/add_subdirectory_test.cmake.in

## Purpose
This CMake template verifies normal `add_subdirectory()` consumption of the zlib source tree from another project.

## Important APIs, Types, and Functions
It defines a small C project, sets `ZLIB_BUILD_TESTING` off, mirrors configured shared/static build options, calls `add_subdirectory(@zlib_SOURCE_DIR@ ${CMAKE_CURRENT_BINARY_DIR}/zlib)`, and conditionally builds example executables linked to `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`.

## Control Flow, State, and Persistence
The parent test configures this template into a generated project, then runs CMake configure and build steps. Shared runtime tests are registered except on `.dll` suffix platforms; static runtime tests are registered whenever static builds are enabled.

## Dependencies and Integration Points
It integrates with `test/CMakeLists.txt`, CTest, the source-tree zlib CMake project, and target aliases exported by the subdirectory build.

## Risks and Test Signals
Risks include stale template substitutions, target alias changes, and the final `endif(@ZLIB_BUILD_STATIC)` substitution becoming malformed if the configured value is unexpected. Passing configure/build and example execution demonstrate that source embedding works without installation.
