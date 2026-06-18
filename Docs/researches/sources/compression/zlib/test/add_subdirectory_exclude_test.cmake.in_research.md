# sources/compression/zlib/test/add_subdirectory_exclude_test.cmake.in

## Purpose
This CMake template verifies that zlib can be consumed via `add_subdirectory(... EXCLUDE_FROM_ALL)` while still exposing usable shared and static targets.

## Important APIs, Types, and Functions
It sets project metadata, disables `ZLIB_BUILD_TESTING`, mirrors configured `ZLIB_BUILD_SHARED` and `ZLIB_BUILD_STATIC`, calls `add_subdirectory(@zlib_SOURCE_DIR@ ... EXCLUDE_FROM_ALL)`, and builds `test_example` and/or `test_example_static` linked to `ZLIB::ZLIB` or `ZLIB::ZLIBSTATIC`.

## Control Flow, State, and Persistence
After substitution by `configure_file()`, CTest configures this as an isolated project. Shared example tests are skipped for `.dll` suffixes, while static examples always register when static builds are enabled. Build output lives only under the generated test build directory.

## Dependencies and Integration Points
It depends on the parent `test/CMakeLists.txt` install/add-subdirectory test fixture, CMake 3.12...3.31, the zlib source tree, and exported in-build CMake targets.

## Risks and Test Signals
Risks include accidental default target pollution despite `EXCLUDE_FROM_ALL`, target export drift, and platform-specific shared-library execution limitations. Passing configure and build tests prove the subdirectory integration path works for enabled library flavors.
