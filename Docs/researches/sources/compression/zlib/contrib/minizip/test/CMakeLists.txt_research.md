# sources/compression/zlib/contrib/minizip/test/CMakeLists.txt

## Purpose
This CMake file defines MiniZip integration tests for installation, CMake package discovery, `add_subdirectory()` consumption, and basic minizip/miniunzip round trips for shared and static builds.

## Important APIs, Types, and Functions
It uses CTest `add_test()` and `set_tests_properties()`, CMake `configure_file()`, generator selection variables, fixtures (`FIXTURES_SETUP`, `FIXTURES_REQUIRED`, `FIXTURES_CLEANUP`), and build options such as `ZLIB_MINIZIP_INSTALL`, `MINIZIP_BUILD_SHARED`, `MINIZIP_BUILD_STATIC`, `MINIZIP_ENABLE_BZIP2`, and `ZLIB_CONTRIB_PREFIX`.

## Control Flow
When install testing is enabled, it optionally installs MiniZip into a test prefix, configures five downstream CMake projects from templates, and runs configure/build tests for package and subdirectory discovery. It marks no-component discovery as expected failure when not both shared and static libraries are built, and always expects the wrong-component test to fail. Separate shared and static blocks prepare test files, run the zipping executable, run the unzip executable, compare extracted output with the original, and clean up using fixtures to enforce order.

## State and Persistence
Tests create configured CMake projects and build directories under `WORK_DIR`, install output under `test_install`, temporary ZIP files, moved/prepared test files, and cleanup artifacts controlled by `test_helper.cm`.

## Dependencies and Integration Points
Integrates the MiniZip build with zlib's top-level CMake variables, generated package config files, installed targets, and the `minizip`, `miniunzip`, `minizipstatic`, and `miniunzipstatic` executables.

## Risks and Edge Cases
The file assumes CMake generator/platform forwarding is sufficient for nested configure runs. Shared executable tests are skipped for `.dll` platforms, reducing Windows coverage. The no-component package test intentionally changes expected outcome based on build variants, so package behavior changes can be masked if build options are not varied in CI. Typos in helper script names would break all round-trip tests.

## Test Signals
This is itself the test orchestration. Strong signals are successful configure/build of exported targets, expected failure for unsupported components, successful ZIP creation/extraction, and exact file comparison for shared/static variants.
