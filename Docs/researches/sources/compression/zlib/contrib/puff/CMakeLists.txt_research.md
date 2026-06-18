# sources/compression/zlib/contrib/puff/CMakeLists.txt

## Purpose
This CMake build script defines the `puff` contrib library, a small deflate decompressor, including shared/static targets, tests, coverage support, install rules, and package exports.

## Important APIs, Types, and Functions
It configures options `ZLIB_PUFF_BUILD_SHARED`, `ZLIB_PUFF_BUILD_STATIC`, `ZLIB_PUFF_BUILD_TESTING`, and `ZLIB_PUFF_INSTALL`; imports zlib components when built standalone; creates aliases `PUFF::PUFF` and `PUFF::PUFFSTATIC`; builds `puff.c`/`puff.h`; creates test helper executable `puff_bin-writer`; installs export files `puff-shared.cmake` and `puff-static.cmake`; and generates `puffConfig.cmake` plus version file.

## Control Flow
When built from zlib, top-level zlib options are copied into puff-specific cache variables. Standalone builds find zlib with required components matching requested shared/static outputs. Testing enables CTest, adjusts compiler flags for coverage discovery on GNU/Clang, builds `bin-writer`, and adds the `test` subdirectory. Shared and static library blocks define targets and properties. Install rules export requested targets, install debug symbols on MSVC where applicable, generate package config files, and install `puff.h`.

## State and Persistence
Persists build targets, generated package config files, install exports, installed headers, and optional test/coverage artifacts. Cache variables control feature state across CMake runs.

## Dependencies and Integration Points
Integrates with zlib's top-level build via `ZLIB_BUILD_PUFF`, `ZLIB_BUILD_SHARED`, `ZLIB_INSTALL`, and `ZLIB_CONTRIB_PREFIX`; with CMake package helpers; with `puff/test`; and with downstream consumers through `PUFF::` imported targets.

## Risks and Edge Cases
Option descriptions mention "blast" in a puff file, suggesting copied text. Resetting `CMAKE_C_FLAGS` during coverage setup can affect tests under this directory. The standalone `find_package(ZLIB REQUIRED COMPONENTS ...)` assumes zlib component exports match `shared` and `static`. Windows naming and PDB install behavior differ by compiler/platform.

## Test Signals
`ZLIB_PUFF_BUILD_TESTING` enables the puff test subdirectory and coverage helper detection. Successful shared/static target builds and package install/export generation are the primary build signals.
