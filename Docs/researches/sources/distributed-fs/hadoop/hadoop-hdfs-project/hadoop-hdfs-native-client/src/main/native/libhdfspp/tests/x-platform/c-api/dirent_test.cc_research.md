<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.cc

## Purpose
Tests directory enumeration for the x-platform dirent abstraction using C API `opendir`/`readdir`/`closedir` wrappers.

## Important APIs, Types, And Functions
Key functions include `DirentTest::SetUp()`, `TearDown()`, `GetTempName()`, `CreateTempDirAndFiles()`, and `ListDirAndFiles()`. Test cases are `DirentCApiTest.TestEmptyFolder`, `DirentCApiTest.TestOneFolder`, `DirentCApiTest.TestOneFile`, `DirentCApiTest.TestMultipleFolders`, `DirentCApiTest.TestMultipleFiles`, `DirentCApiTest.TestOneFileAndFolder`, `DirentCApiTest.TestMultipleFilesAndFolders`.

## Control Flow
Each test creates a temporary root, populates it with a requested number of directories and files, lists direct children through the implementation under test, and compares the unordered set of absolute paths.

## State And Persistence
Runtime state is the temporary root and generated children. `TearDown()` removes the tree.

## Dependencies And Integration Points
Depends on filesystem, gtest, x-platform syscall temp-name helpers, and the dirent abstraction or C API wrapper. These tests validate portability code used by tools that list or glob filesystem entries.

## Risks
The test covers direct children only and does not verify error behavior for permission-denied or deleted-while-iterating directories. Set comparison intentionally ignores ordering.

## Test Signals
Passing all file/folder cardinality combinations indicates the API lists entries without missing files, adding spurious entries, or leaking errno/error states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.cc -->
