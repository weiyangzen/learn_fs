<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `DfMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `DfMock::SetExpectations(std::function<std::unique_ptr<DfMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `DfMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.cc -->
