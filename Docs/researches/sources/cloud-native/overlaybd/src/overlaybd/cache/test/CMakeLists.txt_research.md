<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt -->
# sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt

## Purpose
Builds and registers the generic cache unit test executable.

## Important APIs, Types, And Functions
Adds gflags/gtest include and link directories, creates `cache_test` from `cache_test.cpp`, links gtest, gflags, pthread, `photon_static`, and `overlaybd_lib`, and registers it with CTest.

## Control Flow
CTest invokes the built `cache_test` binary directly.

## State And Persistence
No persistent state in CMake; tests write under `/tmp/ease/cache`.

## Dependencies And Integration Points
Requires environment-provided `GFLAGS` and `GTEST` paths and Photon include settings.

## Risks And Test Signals
The test target is more substantive than the OCF perf target but depends on local filesystem and libaio support. Source size reviewed: 13 lines.
<!-- END_FILE_RESEARCH: sources/cloud-native/overlaybd/src/overlaybd/cache/test/CMakeLists.txt -->
