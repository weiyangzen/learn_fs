# sources/cloud-native/overlaybd/src/overlaybd/lsmt/test/CMakeLists.txt

## Purpose
Defines the LSMT unit/integration test executable `lsmt_test` and registers it with CTest.

## Important APIs and Types
It includes gflags and gtest from environment-provided roots, builds `test.cpp`, exposes Photon includes, and links `gtest`, `gtest_main`, `gflags`, `pthread`, `photon_static`, and `overlaybd_lib`.

## Control Flow
CMake creates the executable and adds a CTest entry invoking `${EXECUTABLE_OUTPUT_PATH}/lsmt_test`.

## State and Persistence
No runtime state is stored here. The test binary itself creates temporary files under `/tmp` through the fixture code.

## Dependencies and Integration Points
Depends on environment variables `GFLAGS` and `GTEST`, plus the broader OverlayBD library target. It is gated by the parent build's testing configuration.

## Risks
Tests will fail to configure if the environment variables or static libraries are missing. Since `test.cpp` includes implementation files directly as well as linking `overlaybd_lib`, duplicate symbol risks depend on how the library is composed.

## Test Signals
Successful configure, build, and CTest registration are the primary signals; runtime coverage comes from `test.cpp`.
