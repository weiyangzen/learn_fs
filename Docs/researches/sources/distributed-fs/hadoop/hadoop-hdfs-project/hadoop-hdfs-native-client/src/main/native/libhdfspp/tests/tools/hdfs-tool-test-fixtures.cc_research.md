<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.cc

## Purpose
Implements the shared HDFS tool test fixtures and their generic parameterized test bodies. It centralizes the assertion policy for all command parser tests.

## Important APIs, Types, And Functions
Out-of-line destructors are defined for `HdfsToolBasicTest`, `HdfsToolNegativeTestThrows`, and `HdfsToolNegativeTestNoThrow`. `TEST_P(HdfsToolBasicTest, RunTool)` expects `Do()` to return true; `TEST_P(HdfsToolNegativeTestNoThrow, RunTool)` expects false; `TEST_P(HdfsToolNegativeTestThrows, RunTool)` expects an exception.

## Control Flow
Fixture setup creates a new command mock from the current parameter. The test body invokes `Do()` exactly once, letting production parsing and gmock expectations determine the result.

## State And Persistence
No persistent state. The only runtime state is the fixture-owned tool object and gmock expectations inside that object.

## Dependencies And Integration Points
Depends on gtest and `hdfs-tool-test-fixtures.h`. It is linked into the tools test binary with all mock files and suite instantiations.

## Risks
The tests are intentionally parser-dispatch tests, not filesystem integration tests. `EXPECT_ANY_THROW` can hide the distinction between expected program_options errors and unexpected implementation exceptions.

## Test Signals
Passing parameterized suites show that command validation, help handling, and handler dispatch remain consistent across all listed HDFS tools.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.cc -->
