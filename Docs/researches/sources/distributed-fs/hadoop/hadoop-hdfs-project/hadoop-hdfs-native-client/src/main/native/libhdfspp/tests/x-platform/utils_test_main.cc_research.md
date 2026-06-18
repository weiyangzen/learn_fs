<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_test_main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_test_main.cc

## Purpose
Provides a Google Test main for x-platform utility and syscall tests that do not use `gtest_main`.

## Important APIs, Types, And Functions
`main()` calls `::testing::InitGoogleTest(&argc, argv)` and returns `RUN_ALL_TESTS()`.

## Control Flow
The executable initializes gtest, runs all linked test cases, and returns the aggregated status.

## State And Persistence
No persistent state.

## Dependencies And Integration Points
Linked into x-platform utility and syscall test executables by the CMake file in this folder.

## Risks
A separate main must not be linked with `gtest_main` in the same executable.

## Test Signals
The process exit code reports the result of all linked x-platform tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_test_main.cc -->
