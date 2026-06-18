<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.h

## Purpose
Defines parameterized Google Test fixtures for exercising `hdfs::tools::HdfsTool` subclasses through a uniform `Do()` call. The fixtures let many command mocks share positive, false-returning negative, and exception-throwing negative test bodies.

## Important APIs, Types, And Functions
`HdfsToolBasicTest` derives from `testing::TestWithParam<std::function<std::unique_ptr<hdfs::tools::HdfsTool>()>>`; `SetUp()` invokes the factory and stores the resulting tool. `HdfsToolNegativeTestThrows` and `HdfsToolNegativeTestNoThrow` specialize the expected failure mode without adding new state.

## Control Flow
Each test parameter is a factory from `hdfs-tool-tests.h`. Before each test, the fixture creates a fresh mock tool with expectations already installed. The companion `.cc` then calls `Do()` and asserts true, false, or any exception according to fixture type.

## State And Persistence
State is one `std::unique_ptr<hdfs::tools::HdfsTool>` per test instance. There is no persistence or external I/O.

## Dependencies And Integration Points
Depends on gtest and the base `hdfs-tool.h` interface. Integrated by `hdfs-tool-tests.cc` through many `INSTANTIATE_TEST_SUITE_P` declarations.

## Risks
Because factories return base-class pointers, typed mock behavior must be installed before upcast. Fixture expectations are broad for exception tests (`EXPECT_ANY_THROW`), so they prove rejection but not the exact exception type.

## Test Signals
Signals are the three parameterized `RunTool` test bodies: success for valid invocations, false for validation paths that should not throw, and any exception for program_options parse failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-test-fixtures.h -->
