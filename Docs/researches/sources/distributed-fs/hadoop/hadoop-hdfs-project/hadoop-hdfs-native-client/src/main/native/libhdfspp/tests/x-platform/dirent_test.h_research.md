<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.h

## Purpose
Declares directory-iteration test fixtures for the x-platform C++ or C API paths.

## Important APIs, Types, And Functions
`DirentTest` owns a temporary root path, `SetUp()`/`TearDown()`, `GetTempName()`, `CreateTempDirAndFiles()`, and virtual `ListDirAndFiles()`. `DirentCApiTest` overrides `ListDirAndFiles()` to use the C API.

## Control Flow
Concrete tests create a temporary root, populate it with numbered directories/files, list children through the API under test, compare unordered sets, and clean up.

## State And Persistence
State is `tmp_root_` during one test. Filesystem side effects are temporary and removed in teardown.

## Dependencies And Integration Points
Depends on gtest, filesystem, `x-platform/dirent.h`, and for C API tests `x-platform/c-api/dirent.h`.

## Risks
Set comparison ignores traversal order, which is appropriate for directory APIs but does not test stable ordering. Cleanup failures can leave temp artifacts.

## Test Signals
Passing empty, one item, and multiple file/directory cases signal directory iteration parity across C++ and C APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.h -->
