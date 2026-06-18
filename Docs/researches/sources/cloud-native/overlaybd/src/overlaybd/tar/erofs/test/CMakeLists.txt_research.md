# sources/cloud-native/overlaybd/src/overlaybd/tar/erofs/test/CMakeLists.txt

## Purpose
Defines EROFS simple and stress test executables and registers them with CTest.

## Important APIs and Types
Builds `erofs_simple_test` from `erofs_simple.cpp` and `erofs_stress_test` from `erofs_stress.cpp erofs_stress_base.cpp`. Both link gtest, pthread, Photon, tar, LSMT, gzip, gzindex, checksum, and overlaybd image libraries.

## Control Flow
CMake creates both executables, adds Photon and RapidJSON include paths, and registers `erofs_simple_test` and `erofs_stress_test` with CTest.

## State and Persistence
The CMake file defines no runtime state. The tests likely create image/tar/layer artifacts through the linked libraries.

## Dependencies and Integration Points
Depends on gflags/gtest environment paths, Photon, tar/EROFS, LSMT, gzip, checksum, and image library targets. It validates the interaction between EROFS conversion and OverlayBD image handling.

## Risks
Environment-provided gtest/gflags paths are required. Stress tests may be resource-intensive depending on their generated data sizes.

## Test Signals
Build and CTest execution of both simple and stress EROFS tests are the key signals.
