# sources/compression/zlib/test/CMakeLists.txt

## Purpose
`test/CMakeLists.txt` defines zlib's CMake test executables and installed-package integration tests.

## Important APIs, Types, and Functions
It defines `ZLIB_findTestEnv(testName)` to prepend the built shared library directory to `PATH` on Windows-like platforms. It creates shared and static `example`, `minigzip`, optional 64-bit examples, optional `infcover` coverage tests, install tests, `find_package()` tests, and `add_subdirectory()` tests using generated CMake projects.

## Control Flow, State, and Persistence
The script conditionally adds targets based on `ZLIB_BUILD_SHARED`, `ZLIB_BUILD_STATIC`, `HAVE_OFF64_T`, compiler ID, coverage tool availability, and `ZLIB_INSTALL`. Install tests use CTest fixtures so configure/build checks depend on the install step. Generated test projects are written with `configure_file()` under the binary tree.

## Dependencies and Integration Points
It depends on imported targets `ZLIB::ZLIB` and `ZLIB::ZLIBSTATIC`, CTest, CMake generator expressions, compiler variables, and template files in the same test directory. It validates both build-tree and install-tree consumption paths.

## Risks and Test Signals
Risks include environment setup for shared libraries on Windows, fixture dependency mistakes, coverage flag side effects, generator/platform quoting, and conditional tests passing vacuously when only one library flavor is built. Strong signals are successful CTest runs for shared/static examples, coverage summary when available, install fixture completion, and expected failure for wrong-component or incomplete no-component package tests.
