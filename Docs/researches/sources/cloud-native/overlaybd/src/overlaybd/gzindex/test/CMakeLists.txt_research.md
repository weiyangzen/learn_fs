<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt

## Purpose
Builds and registers gzip index and gzip cache tests.

## Important APIs, Types, And Functions
Creates `gzindex_test` from `test.cpp`, links gtest/gflags/pthread, Photon, `gzindex_lib`, `gzip_lib`, `cache_lib`, and `checksum_lib`, and adds it as a CTest.

## Control Flow
CTest runs the executable with no extra flags.

## State And Persistence
No CMake runtime state; tests create files under `/tmp`.

## Dependencies And Integration Points
Requires gflags/gtest environment paths and all gzip/cache/checksum libraries.

## Risks And Test Signals
The linked test suite includes network-download stream tests, making it potentially slow/flaky if enabled in ordinary CI. Source size reviewed: 15 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/gzindex/test/CMakeLists.txt -->
