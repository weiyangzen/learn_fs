# Research: subset-b-007439

Grouped research for libhdfs++ HDFS command-line tool parser mocks, shared test fixtures, URI/lock/x-platform utility tests, and the first command build/implementation files in this work item. Each section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `CatMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `CatMock::SetExpectations(std::function<std::unique_ptr<CatMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `CatMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.h

## Purpose
This header declares `CatMock`, a Google Mock subclass of `hdfs::tools::Cat` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`CatMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `CatMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-cat-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `ChgrpMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `ChgrpMock::SetExpectations(std::function<std::unique_ptr<ChgrpMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassOwnerAndAPath`, `PassRecursiveOwnerAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `ChgrpMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.h

## Purpose
This header declares `ChgrpMock`, a Google Mock subclass of `hdfs::tools::Chgrp` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`ChgrpMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, bool, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `ChgrpMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chgrp-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `ChmodMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `ChmodMock::SetExpectations(std::function<std::unique_ptr<ChmodMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassPermissionsAndAPath`, `PassInvalidPermissionsAndAPath`, `PassRecursivePermissionsAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `ChmodMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.h

## Purpose
This header declares `ChmodMock`, a Google Mock subclass of `hdfs::tools::Chmod` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`ChmodMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, bool, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `ChmodMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chmod-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `ChownMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `ChownMock::SetExpectations(std::function<std::unique_ptr<ChownMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassOwnerAndAPath`, `PassRecursiveOwnerAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `ChownMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.h

## Purpose
This header declares `ChownMock`, a Google Mock subclass of `hdfs::tools::Chown` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`ChownMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const Ownership &, bool, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `ChownMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-chown-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `CopyToLocalMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `CopyToLocalMock::SetExpectations(std::function<std::unique_ptr<CopyToLocalMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `Pass2Paths`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `CopyToLocalMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.h

## Purpose
This header declares `CopyToLocalMock`, a Google Mock subclass of `hdfs::tools::CopyToLocal` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`CopyToLocalMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `CopyToLocalMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-copy-to-local-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `CountMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `CountMock::SetExpectations(std::function<std::unique_ptr<CountMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassQOptAndPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `CountMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.h

## Purpose
This header declares `CountMock`, a Google Mock subclass of `hdfs::tools::Count` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`CountMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const bool, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `CountMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-count-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `CreateSnapshotMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `CreateSnapshotMock::SetExpectations(std::function<std::unique_ptr<CreateSnapshotMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassNOptAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `CreateSnapshotMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.h

## Purpose
This header declares `CreateSnapshotMock`, a Google Mock subclass of `hdfs::tools::CreateSnapshot` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`CreateSnapshotMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandleSnapshot, (const std::string &, const std::optional<std::string> &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `CreateSnapshotMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-create-snapshot-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `DeleteSnapshotMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `DeleteSnapshotMock::SetExpectations(std::function<std::unique_ptr<DeleteSnapshotMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `Pass2Paths`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `DeleteSnapshotMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.h

## Purpose
This header declares `DeleteSnapshotMock`, a Google Mock subclass of `hdfs::tools::DeleteSnapshot` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`DeleteSnapshotMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandleSnapshot, (const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `DeleteSnapshotMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-delete-snapshot-mock.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.h

## Purpose
This header declares `DfMock`, a Google Mock subclass of `hdfs::tools::Df` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`DfMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `DfMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-df-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `DisallowSnapshotMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `DisallowSnapshotMock::SetExpectations(std::function<std::unique_ptr<DisallowSnapshotMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `DisallowSnapshotMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.h

## Purpose
This header declares `DisallowSnapshotMock`, a Google Mock subclass of `hdfs::tools::DisallowSnapshot` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`DisallowSnapshotMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandleSnapshot, (const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `DisallowSnapshotMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-disallow-snapshot-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `DuMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `DuMock::SetExpectations(std::function<std::unique_ptr<DuMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassRecursivePath`, `PassRecursive`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `DuMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.h

## Purpose
This header declares `DuMock`, a Google Mock subclass of `hdfs::tools::Du` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`DuMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const bool), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `DuMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-du-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `FindMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `FindMock::SetExpectations(std::function<std::unique_ptr<FindMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassNOptAndAPath`, `PassMOptPermissionsAndAPath`, `PassNStrMNumAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `FindMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.h

## Purpose
This header declares `FindMock`, a Google Mock subclass of `hdfs::tools::Find` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`FindMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const std::string &, uint32_t), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `FindMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-find-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `GetMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `GetMock::SetExpectations(std::function<std::unique_ptr<GetMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `Pass2Paths`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `GetMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.h

## Purpose
This header declares `GetMock`, a Google Mock subclass of `hdfs::tools::Get` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`GetMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `GetMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-get-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `LsMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `LsMock::SetExpectations(std::function<std::unique_ptr<LsMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassRecursivePath`, `PassRecursive`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `LsMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.h

## Purpose
This header declares `LsMock`, a Google Mock subclass of `hdfs::tools::Ls` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`LsMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const bool), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `LsMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-ls-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `MkdirMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `MkdirMock::SetExpectations(std::function<std::unique_ptr<MkdirMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassPOptAndPath`, `PassMOptPermissionsAndAPath`, `PassMPOptsPermissionsAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `MkdirMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.h

## Purpose
This header declares `MkdirMock`, a Google Mock subclass of `hdfs::tools::Mkdir` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`MkdirMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (bool, const std::optional<std::string> &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `MkdirMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-mkdir-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `MoveToLocalMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `MoveToLocalMock::SetExpectations(std::function<std::unique_ptr<MoveToLocalMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `Pass2Paths`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `MoveToLocalMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.h

## Purpose
This header declares `MoveToLocalMock`, a Google Mock subclass of `hdfs::tools::MoveToLocal` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`MoveToLocalMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `MoveToLocalMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-move-to-local-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `RenameSnapshotMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `RenameSnapshotMock::SetExpectations(std::function<std::unique_ptr<RenameSnapshotMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `Pass3Paths`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `RenameSnapshotMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.h

## Purpose
This header declares `RenameSnapshotMock`, a Google Mock subclass of `hdfs::tools::RenameSnapshot` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`RenameSnapshotMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandleSnapshot, (const std::string &, const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `RenameSnapshotMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rename-snapshot-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `RmMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `RmMock::SetExpectations(std::function<std::unique_ptr<RmMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassRecursivePath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `RmMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.h

## Purpose
This header declares `RmMock`, a Google Mock subclass of `hdfs::tools::Rm` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`RmMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const bool, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `RmMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-rm-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `SetrepMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `SetrepMock::SetExpectations(std::function<std::unique_ptr<SetrepMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassPermissionsAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `SetrepMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.h

## Purpose
This header declares `SetrepMock`, a Google Mock subclass of `hdfs::tools::Setrep` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`SetrepMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `SetrepMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-setrep-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `StatMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `StatMock::SetExpectations(std::function<std::unique_ptr<StatMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `StatMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.h

## Purpose
This header declares `StatMock`, a Google Mock subclass of `hdfs::tools::Stat` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`StatMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `StatMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-stat-mock.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.cc

## Purpose
This source file implements the Google Mock expectation setup for `TailMock`, the test double for the matching libhdfs++ command-line tool. It keeps command parsing tests focused on whether `Do()` dispatches to the correct protected virtual handler instead of opening real HDFS connections or touching local files.

## Important APIs, Types, And Functions
The key function is `TailMock::SetExpectations(std::function<std::unique_ptr<TailMock>()>, const std::vector<std::string>&)`. It identifies the template test-case factory by comparing the stored function pointer and then installs `EXPECT_CALL` rules on the mocked handler methods. Covered test factories in this file are: `CallHelp`, `PassAPath`, `PassFOptAndAPath`. The out-of-line destructor anchors the mock vtable.

## Control Flow
Parameterized test factories in `hdfs-tool-tests.h` construct a `TailMock` with synthetic `argc` and `argv`, call `SetExpectations()`, and return the instance to `HdfsToolBasicTest` or a negative fixture. During `Do()`, the real parser runs; if parsing and validation select a command action, the overridden mock handler is expected exactly once with the parsed arguments and returns the configured success or failure value.

## State And Persistence
There is no persisted state. Runtime state is only the Google Mock expectation list bound to one mock object. Static argv strings live in the template factories, while this file consumes the passed argument vector to bind expected values.

## Dependencies And Integration Points
Depends on gtest/gmock, the corresponding production tool header, and shared factory templates from `hdfs-tool-tests.h`. It integrates with `hdfs-tool-tests.cc`, where the same factories are assigned to positive, throwing-negative, or false-returning suites.

## Risks
The function-pointer comparison is brittle: wrapping the factory in another callable would make `target<...>()` return null and fail the assertion. Expectations mirror parser semantics, so any production option signature change requires coordinated updates here and in the factory list. Missing `return` after a matched branch would allow later branches to add unintended expectations; this file uses return only for help in some mocks and relies on mutually exclusive comparisons elsewhere.

## Test Signals
Useful signals are passing parameterized `RunTool` suites, exact `EXPECT_CALL` argument matches for all options, and failure of negative suites when parser validation no longer rejects bad argument combinations. Compile failures also catch mismatched protected handler signatures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.h

## Purpose
This header declares `TailMock`, a Google Mock subclass of `hdfs::tools::Tail` used by libhdfs++ command-line parser tests. The mock exposes the protected handler hooks so tests can verify dispatch without executing real filesystem operations.

## Important APIs, Types, And Functions
`TailMock(int argc, char **argv)` forwards directly to the production base constructor. `SetExpectations(...)` is declared as the bridge between template test-case factories and gmock rules. Mocked methods are: `MOCK_METHOD(bool, HandleHelp, (), (const, override))`; `MOCK_METHOD(bool, HandlePath, (const std::string &, const bool), (const, override))`. Copy and move operations are deleted so each test owns a single expectation-bearing mock instance.

## Control Flow
Tests instantiate `TailMock` through templates in `hdfs-tool-tests.h`. `Do()` is inherited from the production tool and still performs normal program_options parsing and validation. When dispatch reaches `HandleHelp`, `HandlePath`, or `HandleSnapshot`, the mock method intercepts the call and returns the value configured by the companion `.cc` file.

## State And Persistence
The class has no fields beyond inherited `HdfsTool` parser state and gmock internals. It performs no I/O and persists nothing.

## Dependencies And Integration Points
Includes gmock and the corresponding production command header. The declaration must stay ABI/signature compatible with protected virtual methods in the base tool class and with the template factories consumed by `hdfs-tool-tests.cc`.

## Risks
Handler signature drift is the primary risk: a changed constness, argument type, or overload in the production class breaks either override compilation or expectation matching. Because `SetExpectations()` takes a typed `std::function`, adding new factories requires exact template type consistency.

## Test Signals
Successful compilation verifies override signatures. Runtime gmock failures identify parser-dispatch regressions, missing handler calls, duplicate calls, or argument-order mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tail-mock.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc

## Purpose
Instantiates the shared command-line parser tests for libhdfs++ HDFS tools. It maps each command mock to positive and negative factory combinations so the common fixtures can exercise each tool's option grammar.

## Important APIs, Types, And Functions
The file includes every mock header plus `hdfs-tool-test-fixtures.h` and `hdfs-tool-tests.h`. It uses `INSTANTIATE_TEST_SUITE_P` for suites such as `HdfsAllowSnapshot`, `HdfsDisallowSnapshot`, `HdfsRenameSnapshot`, `HdfsCreateSnapshot`, `HdfsCat`, `HdfsDf`, `HdfsDu`, `HdfsLs`, `HdfsDeleteSnapshot`, `HdfsChown`, `HdfsChmod`, `HdfsChgrp` and more, covering help, normal paths, recursive options, numeric options, ownership arguments, snapshot names, and invalid argument counts.

## Control Flow
At test registration time, gtest records factory values for `HdfsToolBasicTest`, `HdfsToolNegativeTestThrows`, and `HdfsToolNegativeTestNoThrow`. At runtime, each factory creates a mock with expectations, the fixture calls `Do()`, and gtest/gmock validates return value or exception behavior.

## State And Persistence
No persistent state. All effects are in-memory gtest registration and per-test mock state.

## Dependencies And Integration Points
Integrates all tool mocks with the shared factory and fixture framework. It is compiled into the tools test executable alongside `main.cc`.

## Risks
This is the central coverage matrix; omissions here mean a parser branch can be untested even if a factory and mock branch exist. Many negative cases expect broad exceptions from Boost program_options rather than specific diagnostics.

## Test Signals
The signal is suite-level coverage across each command. Failures reveal changed accepted arity, option aliases, parser exception behavior, or dispatch argument order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h

## Purpose
Provides reusable template factories that create command mocks with specific synthetic command lines. Each factory configures expectations before returning the mock as the parameter for shared `HdfsTool` fixtures.

## Important APIs, Types, And Functions
Factories include `PassAPath`, `PassRecursive`, `PassRecursivePath`, `PassFOptAndAPath`, `CallHelp`, `Pass2Paths`, `Pass3Paths`, `PassNOptAndAPath`, `PassOwnerAndAPath`, `PassRecursiveOwnerAndAPath`, `PassPermissionsAndAPath`, `PassInvalidPermissionsAndAPath`, `PassRecursivePermissionsAndAPath`, `PassQOpt`, `PassQOptAndPath`, `PassPOpt`, `PassMOpt`, `PassFOpt`, `PassPOptAndPath`, `PassMOptPermissionsAndAPath`, `PassMPOptsPermissionsAndAPath`, `PassNStrMNumAndAPath`, `PassNOpt`. They build static `std::string` argv storage, assemble `char *argv[]`, construct `T(argc, argv)`, and call `SetExpectations()` with the factory identity plus argument values.

## Control Flow
`hdfs-tool-tests.cc` chooses these factories for each tool and fixture type. The factory encodes the command-line shape; the mock-specific `SetExpectations()` encodes the handler that should be reached after production parsing.

## State And Persistence
State is limited to static strings used as stable argv backing storage. There is no persistence and no filesystem activity.

## Dependencies And Integration Points
Depends only on standard strings and memory, but it is tightly coupled to every mock's `SetExpectations()` overload and every production tool's option grammar.

## Risks
Static argv buffers are shared across tests but contain immutable test values, so they are acceptable for normal gtest execution. The exact factory pointer is used for expectation dispatch, making refactoring to lambdas or bind expressions risky. New command options need matching factory and mock branches.

## Test Signals
Compilation verifies every mock accepts the factory signature. Runtime suite failures pinpoint parser changes through unexpected throws, false returns, or unmet mock calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/hdfs-tool-tests.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/main.cc

## Purpose
Provides the test executable entry point for the HDFS tool parser/mock test suite.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` calls `::testing::InitGoogleMock(&argc, argv)` and returns `RUN_ALL_TESTS()`.

## Control Flow
Process startup enters this file, initializes gtest/gmock command-line handling, runs all registered parameterized suites from `hdfs-tool-tests.cc`, and returns the aggregate test status.

## State And Persistence
No persistent state. Runtime state is owned by Google Test.

## Dependencies And Integration Points
Depends on gmock/gtest and links with all mock, fixture, and suite-instantiation objects.

## Risks
Using `InitGoogleMock` rather than only `InitGoogleTest` is necessary because mocks are used throughout the suite. A missing or duplicated main would break test binary linkage.

## Test Signals
The executable exit code is the test signal; nonzero means at least one parser/mock suite failed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/tools/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc

## Purpose
Tests the libhdfs++ `hdfs::URI` parser, encoder, mutators, query helpers, and error reporting for ordinary HDFS paths and encoded URI components.

## Important APIs, Types, And Functions
Helpers `expect_uri_throw()` and `expect_uri_nothrow()` wrap `URI::parse_from_string()` and assert exception behavior. Test cases cover `UriTest.TestDegenerateInputs`, `UriTest.TestNominalInputs`, `UriTest.TestEncodedInputs`, `UriTest.TestDecodedInputsAndOutputs`, `UriTest.TestSetters`, `UriTest.QueryManip`. Assertions exercise `get_scheme`, `get_host`, port accessors, `get_path`, encoded getters, `get_path_elements`, `get_query_elements`, setters, `add_path`, `add_query`, `remove_query`, and `str()`.

## Control Flow
Each test parses or constructs a URI, then checks decoded and encoded views. Negative helpers verify `uri_parse_error::what()` carries the original malformed string. The local `main()` initializes Google Mock and runs all tests.

## State And Persistence
Only stack-local URI objects and temporary strings are used. No persistence or filesystem state.

## Dependencies And Integration Points
Depends on `hdfspp/uri.h`, gtest, and gmock. It validates behavior relied on by every HDFS command tool that calls `parse_path_or_exit()`.

## Risks
The tests codify specific encoding semantics such as plus-to-space in paths and encoded query handling. Missing cases include IPv6 authorities, userinfo, and unusual path normalization. Error tests check only selected malformed inputs.

## Test Signals
Passing tests signal stable URI parsing, encoding round trips, query manipulation, and malformed-input exception behavior for command-line path handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/uri_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/user_lock_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/user_lock_test.cc

## Purpose
Tests libhdfs++ user-provided lock abstraction behavior, including default mutex operation, one-time lock-manager initialization, failure propagation, RAII locking, and concurrent guarded updates.

## Important APIs, Types, And Functions
`CantLockMutex` implements `Mutex` with throwing `lock()` and `unlock()`. Tests use `LockManager::TEST_get_default_mutex()`, `LockManager::getGssapiMutex()`, `LockManager::InitLocks()`, `LockManager::TEST_reset_manager()`, `LockGuard`, `LockFailure`, and worker functors `Incrementer`/`Decrementer`.

## Control Flow
Tests first validate basic lock/unlock. They then install a custom mutex, verify double initialization fails until test reset, assert throwing behavior for an unusable mutex, and run repeated RAII lock attempts. The concurrency test launches paired increment and decrement threads guarded by the default mutex and expects the final counter to return to zero.

## State And Persistence
State includes the process-global `LockManager` mutex pointer during tests and stack/local counters. `TEST_reset_manager()` restores default global state; nothing persists outside the process.

## Dependencies And Integration Points
Depends on `hdfspp/locks.h`, gtest/gmock, `<thread>`, and standard synchronization types. It validates the lock hooks used around security/GSSAPI integration in libhdfs++.

## Risks
The high-iteration concurrency test can be slow on constrained systems but gives meaningful race coverage. The custom bad mutex verifies exception propagation but does not test unlock failure after a successful lock.

## Test Signals
Passing tests show default locking works repeatedly, custom lock installation is single-use unless reset, `LockGuard` handles failures, and mutex protection prevents lost updates under concurrent access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/user_lock_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/CMakeLists.txt

## Purpose
Builds the small `tests/utils` object library used by libhdfs++ tests.

## Important APIs, Types, And Functions
CMake declarations: `add_library(test_utils OBJECT $<TARGET_OBJECTS:x_platform_obj> temp-file.cc temp-dir.cc)`.

## Control Flow
During CMake configuration this file contributes an object library named `test_utils` that combines the x-platform object code with `temp-file.cc` and `temp-dir.cc`.

## State And Persistence
No runtime state. Build output is an object library consumed by test targets.

## Dependencies And Integration Points
Depends on the previously defined `x_platform_obj` target and the temporary file/directory helper sources in this folder.

## Risks
If `x_platform_obj` is not defined before this directory is processed, configuration fails. Object-library reuse means downstream tests inherit x-platform compile settings.

## Test Signals
Successful CMake generation and downstream test linking show the helper library is available.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc

## Purpose
Implements `TestUtils::TempDir`, an RAII helper that creates a temporary directory for tests and removes it recursively on destruction.

## Important APIs, Types, And Functions
The default constructor builds a mutable template from `path_`, calls `XPlatform::Syscall::CreateTempDir()`, asserts success with gtest, and stores the actual path. Copy/move assignment update `path_`; the destructor calls `std::filesystem::remove_all()`.

## Control Flow
Construction creates the temp directory before tests use it. Destruction exits early if initialization failed; otherwise it removes the directory tree and emits stderr diagnostics when removal fails.

## State And Persistence
State is `path_` and `is_path_init_`. Persistent filesystem state is temporary and intended to be deleted in the destructor.

## Dependencies And Integration Points
Depends on `utils/temp-dir.h`, `x-platform/syscall.h`, gtest assertions, and C++17 filesystem. Used by tests needing isolated directories.

## Risks
Move construction does not transfer `is_path_init_`, so a moved-to object may not clean up an initialized path while the moved-from object may clean an empty or moved path depending on string state. Copying can duplicate cleanup ownership.

## Test Signals
Signals are successful temp directory creation and absence of leftover temporary directories after tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h

## Purpose
Declares `TestUtils::TempDir`, a test RAII wrapper around a temporary directory rooted by default under `/tmp`.

## Important APIs, Types, And Functions
Public API includes default construction, copy/move constructors and assignment, `GetPath()`, and destructor cleanup. Private state is a path template string and an initialization flag.

## Control Flow
Consumers construct a `TempDir`, use `GetPath()` to create files under it, and rely on the destructor to recursively delete the directory tree.

## State And Persistence
The object owns a temporary filesystem path while alive. Cleanup is best effort through the implementation file.

## Dependencies And Integration Points
The header is standalone except for `<string>` and is implemented by `temp-dir.cc` using x-platform temp-directory creation.

## Risks
Defaulted copy construction can create multiple owners for the same directory path, while move handling needs careful ownership semantics. Tests should avoid copying unless duplicate cleanup is acceptable.

## Test Signals
Compilation of tests using `GetPath()` and clean teardown of temporary directories validate the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-dir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc

## Purpose
Implements `TestUtils::TempFile`, an RAII helper that creates a temporary file, tracks its descriptor and filename, closes it, and unlinks it on destruction.

## Important APIs, Types, And Functions
The default constructor calls `XPlatform::Syscall::CreateAndOpenTempFile()` on a mutable filename template. The alternate constructor wraps an existing filename without opening it. Copy/move assignment copy the filename and descriptor. The destructor calls `XPlatform::Syscall::CloseFile()` when `fd_ != -1` and then `unlink()`.

## Control Flow
Construction creates or records the file. Tests obtain the name through `GetFileName()`. Destruction closes the descriptor and removes the path.

## State And Persistence
State is `filename_` plus `fd_`. Persistent local filesystem state exists only for the helper lifetime, assuming destructor cleanup succeeds.

## Dependencies And Integration Points
Depends on `utils/temp-file.h`, x-platform syscall helpers, gtest assertions, and POSIX-style `unlink`.

## Risks
Copying duplicates the raw file descriptor value and can cause double-close. Move construction does not invalidate the source descriptor, so moved objects also risk double-close. The explicit filename constructor unlinks the path even when it did not open it.

## Test Signals
Signals are successful temp-file creation, valid descriptors, successful close, and no leftover files after tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h

## Purpose
Declares `TestUtils::TempFile`, a test helper that owns a temporary file path and, normally, an open descriptor.

## Important APIs, Types, And Functions
Public API includes default construction, construction from a filename, copy/move constructors and assignments, `GetFileName()`, and destructor cleanup. Private fields are `filename_` and `fd_`.

## Control Flow
Tests instantiate the helper, pass `GetFileName()` to code under test, and rely on destruction to close/unlink the file.

## State And Persistence
The object owns temporary local filesystem state while alive. Persistence is meant to end when the destructor runs.

## Dependencies And Integration Points
Implemented by `temp-file.cc` using `XPlatform::Syscall` temp-file and close wrappers.

## Risks
Copy and move declarations expose raw descriptor ownership hazards unless implementation invalidates moved/copied sources, which it currently does not.

## Test Signals
Successful helper construction and cleanup are the main signals; sanitizer or OS-level double-close diagnostics would reveal ownership bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/utils/temp-file.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt

## Purpose
Defines libhdfs++ x-platform unit-test targets for path utilities, syscall wrappers, `ssize_t` compatibility, and directory iteration including the C API wrapper.

## Important APIs, Types, And Functions
CMake declarations: `add_executable(x_platform_utils_test $<TARGET_OBJECTS:x_platform_obj> utils_common_test.cc utils_test_main.cc utils_win_test.cc)`, `add_executable(x_platform_syscall_test $<TARGET_OBJECTS:x_platform_obj> syscall_common_test.cc utils_test_main.cc syscall_win_test.cc)`, `add_executable(x_platform_utils_test $<TARGET_OBJECTS:x_platform_obj> utils_common_test.cc utils_test_main.cc utils_nix_test.cc)`, `add_executable(x_platform_syscall_test $<TARGET_OBJECTS:x_platform_obj> syscall_common_test.cc utils_test_main.cc syscall_nix_test.cc)`, `target_include_directories(x_platform_utils_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_utils_test gmock_main)`, `add_test(x_platform_utils_test x_platform_utils_test)`, `target_include_directories(x_platform_syscall_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_syscall_test gmock_main)`, `add_test(x_platform_syscall_test x_platform_syscall_test)`, `add_executable(x_platform_types_test types_test.cc)`, `target_include_directories(x_platform_types_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_types_test gtest_main)`, `add_test(x_platform_types_test x_platform_types_test)`, `add_library(x_platform_dirent_test_obj OBJECT $<TARGET_OBJECTS:x_platform_obj> dirent_test.cc)`, `add_executable(x_platform_dirent_test $<TARGET_OBJECTS:x_platform_dirent_test_obj> $<TARGET_OBJECTS:x_platform_obj>)`, `target_include_directories(x_platform_dirent_test PRIVATE ${LIBHDFSPP_LIB_DIR})`, `target_link_libraries(x_platform_dirent_test PRIVATE gtest_main)`, `add_test(x_platform_dirent_test x_platform_dirent_test)`, `add_executable(x_platform_dirent_c_test $<TARGET_OBJECTS:x_platform_dirent_test_obj> $<TARGET_OBJECTS:x_platform_obj> $<TARGET_OBJECTS:x_platform_obj_c_api> c-api/dirent_test.cc)`, `target_compile_definitions(x_platform_dirent_c_test PRIVATE USE_X_PLATFORM_DIRENT)`, `target_include_directories(x_platform_dirent_c_test PRIVATE ${LIBHDFSPP_LIB_DIR} ../)`, `target_link_libraries(x_platform_dirent_c_test PRIVATE gtest_main)`, `add_test(x_platform_dirent_c_test x_platform_dirent_c_test)`.

## Control Flow
CMake selects Windows or non-Windows source files for utils and syscall tests, then registers each executable with `add_test`. Directory iteration tests reuse an object library and build both C++ and C API test executables.

## State And Persistence
No runtime state. Build state consists of test executables and object libraries.

## Dependencies And Integration Points
Depends on `x_platform_obj`, `x_platform_obj_c_api`, gtest/gmock, and `${LIBHDFSPP_LIB_DIR}` includes.

## Risks
Platform branches must remain symmetric as x-platform APIs evolve. Reusing object libraries requires compatible compile definitions, especially `USE_X_PLATFORM_DIRENT` for the C API test.

## Test Signals
Successful configure/build plus registered CTest targets `x_platform_utils_test`, `x_platform_syscall_test`, `x_platform_types_test`, `x_platform_dirent_test`, and `x_platform_dirent_c_test`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.h

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/c-api/dirent_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.cc

## Purpose
Tests directory enumeration for the x-platform dirent abstraction using C++ `XPlatform::Dirent::NextFile()` variant API.

## Important APIs, Types, And Functions
Key functions include `DirentTest::SetUp()`, `TearDown()`, `GetTempName()`, `CreateTempDirAndFiles()`, and `ListDirAndFiles()`. Test cases are `DirentTest.TestEmptyFolder`, `DirentTest.TestOneFolder`, `DirentTest.TestOneFile`, `DirentTest.TestMultipleFolders`, `DirentTest.TestMultipleFiles`, `DirentTest.TestOneFileAndFolder`, `DirentTest.TestMultipleFilesAndFolders`.

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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/dirent_test.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc

## Purpose
Tests x-platform syscall helper behavior for wildcard matching, secure buffer clearing, case-insensitive string comparison, temporary file/directory creation, and platform path separators.

## Important APIs, Types, And Functions
Tested functions include `XPlatform::Syscall::FnMatch`, `ClearBufferSafely`, `StringCompareIgnoreCase`, `CreateAndOpenTempFile`, `CloseFile`, and `CreateTempDir`. Test cases are `XPlatformSyscall.FnMatchBasicAsterisk`, `XPlatformSyscall.FnMatchBasicQuestionMark`, `XPlatformSyscall.FnMatchNegativeAsterisk`, `XPlatformSyscall.FnMatchNegativeQuestionMark`, `XPlatformSyscall.ClearBufferSafelyChars`, `XPlatformSyscall.ClearBufferSafelyNumbers`, `XPlatformSyscall.StringCompareIgnoreCaseBasic`, `XPlatformSyscall.StringCompareIgnoreCaseNegative`, `XPlatformSyscall.CreateAndOpenTempFileBasic`, `XPlatformSyscall.CreateAndOpenTempFileNegative`, `XPlatformSyscall.CreateTempDirBasic`, `XPlatformSyscall.CreateTempDirNegative`.

## Control Flow
Common tests run on every platform; `syscall_nix_test.cc` and `syscall_win_test.cc` add path separator specific wildcard behavior. Temp helpers mutate pattern buffers and return descriptors or booleans that are asserted.

## State And Persistence
Temporary files/directories may be created during tests; descriptors are closed. Buffers and strings are stack/local state.

## Dependencies And Integration Points
Depends on gtest and `x-platform/syscall.h`. It validates low-level wrappers used by temp utilities, directory tests, and path-matching logic.

## Risks
Temporary directory tests may leave directories if cleanup is not performed by the wrapper or OS. Wildcard semantics can differ between native APIs, so platform-specific tests guard separator behavior.

## Test Signals
Passing tests show consistent wildcard matching, zeroing, temp resource creation failure handling, and case-insensitive comparison across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_common_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_nix_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_nix_test.cc

## Purpose
Tests x-platform syscall helper behavior for wildcard matching, secure buffer clearing, case-insensitive string comparison, temporary file/directory creation, and platform path separators.

## Important APIs, Types, And Functions
Tested functions include `XPlatform::Syscall::FnMatch`, `ClearBufferSafely`, `StringCompareIgnoreCase`, `CreateAndOpenTempFile`, `CloseFile`, and `CreateTempDir`. Test cases are `XPlatformSyscall.FnMatchBasicPath`, `XPlatformSyscall.FnMatchNegativePath`.

## Control Flow
Common tests run on every platform; `syscall_nix_test.cc` and `syscall_win_test.cc` add path separator specific wildcard behavior. Temp helpers mutate pattern buffers and return descriptors or booleans that are asserted.

## State And Persistence
Temporary files/directories may be created during tests; descriptors are closed. Buffers and strings are stack/local state.

## Dependencies And Integration Points
Depends on gtest and `x-platform/syscall.h`. It validates low-level wrappers used by temp utilities, directory tests, and path-matching logic.

## Risks
Temporary directory tests may leave directories if cleanup is not performed by the wrapper or OS. Wildcard semantics can differ between native APIs, so platform-specific tests guard separator behavior.

## Test Signals
Passing tests show consistent wildcard matching, zeroing, temp resource creation failure handling, and case-insensitive comparison across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_nix_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_win_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_win_test.cc

## Purpose
Tests x-platform syscall helper behavior for wildcard matching, secure buffer clearing, case-insensitive string comparison, temporary file/directory creation, and platform path separators.

## Important APIs, Types, And Functions
Tested functions include `XPlatform::Syscall::FnMatch`, `ClearBufferSafely`, `StringCompareIgnoreCase`, `CreateAndOpenTempFile`, `CloseFile`, and `CreateTempDir`. Test cases are `XPlatformSyscall.FnMatchBasicPath`, `XPlatformSyscall.FnMatchNegativePath`.

## Control Flow
Common tests run on every platform; `syscall_nix_test.cc` and `syscall_win_test.cc` add path separator specific wildcard behavior. Temp helpers mutate pattern buffers and return descriptors or booleans that are asserted.

## State And Persistence
Temporary files/directories may be created during tests; descriptors are closed. Buffers and strings are stack/local state.

## Dependencies And Integration Points
Depends on gtest and `x-platform/syscall.h`. It validates low-level wrappers used by temp utilities, directory tests, and path-matching logic.

## Risks
Temporary directory tests may leave directories if cleanup is not performed by the wrapper or OS. Wildcard semantics can differ between native APIs, so platform-specific tests guard separator behavior.

## Test Signals
Passing tests show consistent wildcard matching, zeroing, temp resource creation failure handling, and case-insensitive comparison across platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/syscall_win_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.cc

## Purpose
Instantiates the typed x-platform type tests for `ssize_t`.

## Important APIs, Types, And Functions
`INSTANTIATE_TYPED_TEST_SUITE_P(SSizeTTest, XPlatformTypesTest, ssize_t)` binds the generic tests from `types_test.h` to the platform `ssize_t` typedef from `x-platform/types.h`.

## Control Flow
Google Test expands the registered typed tests at compile/test registration time and runs them under the `SSizeTTest` prefix.

## State And Persistence
No runtime state beyond test registration.

## Dependencies And Integration Points
Depends on `types_test.h` and `x-platform/types.h`, ensuring the compatibility typedef works on Windows and Unix-like builds.

## Risks
If `ssize_t` is incorrectly typedefed, compile-time numeric-limit expectations fail. This file only instantiates one type.

## Test Signals
Passing typed tests show `ssize_t` can represent `-1`, at least `int`, and on 64-bit builds at least `long int`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h

## Purpose
Defines typed Google Tests for x-platform signed size type compatibility.

## Important APIs, Types, And Functions
`XPlatformTypesTest<T>` is the typed fixture. Registered tests are `SSizeTMinusOne`, `SSizeTCanHoldInts`, and on 64-bit systems `SSizeTCanHoldLongInts`, all using `std::numeric_limits`.

## Control Flow
The header registers typed test patterns; `types_test.cc` instantiates them for `ssize_t`.

## State And Persistence
No mutable state and no persistence.

## Dependencies And Integration Points
Depends on gtest and standard limits. It validates the public x-platform type contract consumed by filesystem and syscall wrappers.

## Risks
Architecture detection uses preprocessor checks for `_WIN64`, `__x86_64__`, and `__ppc64__`; other 64-bit architectures may skip the long-int capacity test.

## Test Signals
Passing tests confirm the signed size type can represent sentinel negative values and expected positive ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/types_test.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc

## Purpose
Tests `XPlatform::Utils::Basename()` behavior for common, Unix-specific, or Windows-specific path forms.

## Important APIs, Types, And Functions
The tested API is `XPlatform::Utils::Basename`. Test cases are `XPlatformUtils.BasenameEmpty`, `XPlatformUtils.BasenameRelativePath`, `XPlatformUtils.BasenameSpecialFiles`.

## Control Flow
Each test passes a representative path string and compares the returned basename to the expected platform-specific value.

## State And Persistence
No state beyond local strings.

## Dependencies And Integration Points
Depends on gtest and `x-platform/utils.h`. These semantics are used by tools and tests that need portable path basename behavior.

## Risks
Platform-specific expectations can drift if path handling is changed to normalize more aggressively. Empty path and root path behavior are explicitly part of the contract.

## Test Signals
Passing tests indicate basename handling for empty paths, relative paths, dot entries, roots, trailing separators, and normal nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_common_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_nix_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_nix_test.cc

## Purpose
Tests `XPlatform::Utils::Basename()` behavior for common, Unix-specific, or Windows-specific path forms.

## Important APIs, Types, And Functions
The tested API is `XPlatform::Utils::Basename`. Test cases are `XPlatformUtils.BasenameRoot`, `XPlatformUtils.BasenameTrailingSlash`, `XPlatformUtils.BasenameBasic`.

## Control Flow
Each test passes a representative path string and compares the returned basename to the expected platform-specific value.

## State And Persistence
No state beyond local strings.

## Dependencies And Integration Points
Depends on gtest and `x-platform/utils.h`. These semantics are used by tools and tests that need portable path basename behavior.

## Risks
Platform-specific expectations can drift if path handling is changed to normalize more aggressively. Empty path and root path behavior are explicitly part of the contract.

## Test Signals
Passing tests indicate basename handling for empty paths, relative paths, dot entries, roots, trailing separators, and normal nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_nix_test.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_win_test.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_win_test.cc

## Purpose
Tests `XPlatform::Utils::Basename()` behavior for common, Unix-specific, or Windows-specific path forms.

## Important APIs, Types, And Functions
The tested API is `XPlatform::Utils::Basename`. Test cases are `XPlatformUtils.BasenameRoot`, `XPlatformUtils.BasenameRootLabel`, `XPlatformUtils.BasenameTrailingSlash`, `XPlatformUtils.BasenameBasic`.

## Control Flow
Each test passes a representative path string and compares the returned basename to the expected platform-specific value.

## State And Persistence
No state beyond local strings.

## Dependencies And Integration Points
Depends on gtest and `x-platform/utils.h`. These semantics are used by tools and tests that need portable path basename behavior.

## Risks
Platform-specific expectations can drift if path handling is changed to normalize more aggressively. Empty path and root path behavior are explicitly part of the contract.

## Test Signals
Passing tests indicate basename handling for empty paths, relative paths, dot entries, roots, trailing separators, and normal nested paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/x-platform/utils_win_test.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt

## Purpose
Top-level CMake build script for libhdfs++ command-line tools. It discovers Boost program_options, configures include/link roots, builds shared helper objects, and adds every individual HDFS command subdirectory.

## Important APIs, Types, And Functions
CMake declarations: `find_package(Boost 1.86 COMPONENTS program_options REQUIRED)`, `add_library(tools_common_obj OBJECT tools_common.cc)`, `add_library(tools_common $<TARGET_OBJECTS:tools_common_obj>)`, `add_subdirectory(internal)`, `add_library(hdfs_tool_obj OBJECT hdfs-tool.cc)`, `target_include_directories(hdfs_tool_obj PRIVATE ../tools)`, `add_subdirectory(hdfs-cat)`, `add_subdirectory(hdfs-chgrp)`, `add_subdirectory(hdfs-chown)`, `add_subdirectory(hdfs-chmod)`, `add_subdirectory(hdfs-find)`, `add_subdirectory(hdfs-mkdir)`, `add_subdirectory(hdfs-rm)`, `add_subdirectory(hdfs-ls)`, `add_subdirectory(hdfs-stat)`, `add_subdirectory(hdfs-count)`, `add_subdirectory(hdfs-df)`, `add_subdirectory(hdfs-du)`, `add_subdirectory(hdfs-get)`, `add_subdirectory(hdfs-copy-to-local)`, `add_subdirectory(hdfs-move-to-local)`, `add_subdirectory(hdfs-setrep)`, `add_subdirectory(hdfs-allow-snapshot)`, `add_subdirectory(hdfs-disallow-snapshot)`, `add_subdirectory(hdfs-create-snapshot)`, `add_subdirectory(hdfs-rename-snapshot)`, `add_subdirectory(hdfs-delete-snapshot)`, `add_subdirectory(hdfs-tail)`.

## Control Flow
CMake first resolves Boost and `LIBHDFSPP_DIR`, exposes include and link directories, creates `tools_common_obj/tools_common`, includes internal helper code, creates the shared `hdfs_tool_obj`, then processes each command subdirectory from `hdfs-cat` through `hdfs-tail`.

## State And Persistence
No runtime state. Build state is object libraries, command static libraries, and executable targets registered by child directories.

## Dependencies And Integration Points
Integrates the tool tree with installed libhdfs++ headers/libs, Boost program_options, common helpers, and all child command CMake files.

## Risks
Global `include_directories()` and `link_directories()` affect all child targets and can hide missing target-specific dependencies. Adding a new tool requires both a subdirectory and matching tests/install rules.

## Test Signals
Successful configuration and build of all command executable targets, plus parser test linkage against the same command libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/CMakeLists.txt

## Purpose
Builds the `hdfs-allow-snapshot` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_allowSnapshot_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> hdfs-allow-snapshot.cc)`, `target_include_directories(hdfs_allowSnapshot_lib PRIVATE ../../tools ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_allowSnapshot_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_allowSnapshot main.cc)`, `target_include_directories(hdfs_allowSnapshot PRIVATE ../../tools)`, `target_link_libraries(hdfs_allowSnapshot PRIVATE hdfs_allowSnapshot_lib)`, `install(TARGETS hdfs_allowSnapshot RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.cc

## Purpose
Implements `hdfs_allowsnapshot`, making an hdfs directory snapshottable.

## Important APIs, Types, And Functions
The implementation defines `AllowSnapshot::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `AllowSnapshot` derives from `HdfsTool`; `HandlePath()` parses the URI, connects through `doConnect()`, and calls `FileSystem::AllowSnapshot()`.

## Control Flow
Boost program_options accepts optional `-h` and one positional path. `Do()` validates argument count, handles help, then dispatches the parsed path to `HandlePath()`. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
No persistent local state beyond `HdfsTool` option maps and positional options. The durable effect is the NameNode snapshot permission change. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Argument validation allows any single non-help path and depends on `parse_path_or_exit()` for URI failures. Runtime failure surfaces through returned `Status` and stderr. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.h

## Purpose
Declares `AllowSnapshot`, the `HdfsTool` implementation for `hdfs-allow-snapshot`. implements `hdfs_allowSnapshot`, making an HDFS directory snapshottable.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `AllowSnapshot` derives from `HdfsTool`; `HandlePath()` parses the URI, connects through `doConnect()`, and calls `FileSystem::AllowSnapshot()`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. No persistent local state beyond `HdfsTool` option maps and positional options. The durable effect is the NameNode snapshot permission change.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Argument validation allows any single non-help path and depends on `parse_path_or_exit()` for URI failures. Runtime failure surfaces through returned `Status` and stderr.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/hdfs-allow-snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/main.cc

## Purpose
Provides the executable entry point for `hdfs-allow-snapshot`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::AllowSnapshot`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-allow-snapshot/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/CMakeLists.txt

## Purpose
Builds the `hdfs-cat` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_cat_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> hdfs-cat.cc)`, `target_include_directories(hdfs_cat_lib PRIVATE ../../tools hdfs-cat ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_cat_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_cat main.cc)`, `target_include_directories(hdfs_cat PRIVATE ../../tools)`, `target_link_libraries(hdfs_cat PRIVATE hdfs_cat_lib)`, `install(TARGETS hdfs_cat RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.cc

## Purpose
Implements `hdfs_cat`, streaming one hdfs file to standard output.

## Important APIs, Types, And Functions
The implementation defines `Cat::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Cat` derives from `HdfsTool`; `HandlePath()` parses a path, connects without max timeout, and calls `readFile(fs, path, 0, stdout, false)`.

## Control Flow
The command accepts `-h` or one positional file. Successful non-help execution opens the remote file through shared helpers and streams it from offset zero. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
No persistent state. Output is written to stdout; HDFS state is read-only. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
`readFile()` return value is not checked here, so stream failures depend on helper-side diagnostics. Multiple positional arguments are rejected by program_options. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.h

## Purpose
Declares `Cat`, the `HdfsTool` implementation for `hdfs-cat`. implements `hdfs_cat`, streaming one HDFS file to standard output.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `Cat` derives from `HdfsTool`; `HandlePath()` parses a path, connects without max timeout, and calls `readFile(fs, path, 0, stdout, false)`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. No persistent state. Output is written to stdout; HDFS state is read-only.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. `readFile()` return value is not checked here, so stream failures depend on helper-side diagnostics. Multiple positional arguments are rejected by program_options.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/hdfs-cat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/main.cc

## Purpose
Provides the executable entry point for `hdfs-cat`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Cat`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-cat/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt

## Purpose
Builds the `hdfs-chgrp` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_chgrp_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> $<TARGET_OBJECTS:hdfs_ownership_obj> hdfs-chgrp.cc)`, `target_include_directories(hdfs_chgrp_lib PRIVATE ../../tools hdfs-chgrp ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_chgrp_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_chgrp main.cc)`, `target_include_directories(hdfs_chgrp PRIVATE ../../tools)`, `target_link_libraries(hdfs_chgrp PRIVATE hdfs_chgrp_lib)`, `install(TARGETS hdfs_chgrp RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.cc

## Purpose
Implements `hdfs_chgrp`, changing the group for one path or a recursive listing.

## Important APIs, Types, And Functions
The implementation defines `Chgrp::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Chgrp` derives from `HdfsTool`; `HandlePath(group, recursive, file)` calls `FileSystem::SetOwner(path, "", group, handler)` and uses `OwnerState` for recursive fan-out.

## Control Flow
Options parse `-R`, group, and file. Non-recursive mode sends one async `SetOwner`; recursive mode calls `Find()` and launches one async `SetOwner` per result, completing a promise when find and all requests finish. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
Runtime state is `OwnerState`: target group, completion handler, request counter, first error status, find completion flag, and mutex. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Recursive completion depends on accurate request counting across callbacks. First error wins, later errors are suppressed. Empty recursive results complete only after `Find()` reports no more results. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.h

## Purpose
Declares `Chgrp`, the `HdfsTool` implementation for `hdfs-chgrp`. implements `hdfs_chgrp`, changing the group for one path or a recursive listing.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `Chgrp` derives from `HdfsTool`; `HandlePath(group, recursive, file)` calls `FileSystem::SetOwner(path, "", group, handler)` and uses `OwnerState` for recursive fan-out.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. Runtime state is `OwnerState`: target group, completion handler, request counter, first error status, find completion flag, and mutex.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Recursive completion depends on accurate request counting across callbacks. First error wins, later errors are suppressed. Empty recursive results complete only after `Find()` reports no more results.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/hdfs-chgrp.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/main.cc

## Purpose
Provides the executable entry point for `hdfs-chgrp`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Chgrp`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chgrp/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/CMakeLists.txt

## Purpose
Builds the `hdfs-chmod` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_chmod_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> $<TARGET_OBJECTS:hdfs_ownership_obj> hdfs-chmod.cc)`, `target_include_directories(hdfs_chmod_lib PRIVATE ../../tools hdfs-chmod ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_chmod_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_chmod main.cc)`, `target_include_directories(hdfs_chmod PRIVATE ../../tools)`, `target_link_libraries(hdfs_chmod PRIVATE hdfs_chmod_lib)`, `install(TARGETS hdfs_chmod RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc

## Purpose
Implements `hdfs_chmod`, setting octal permissions for one path or a recursive listing.

## Important APIs, Types, And Functions
The implementation defines `Chmod::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Chmod` derives from `HdfsTool`; `HandlePath(permissions, recursive, file)` validates octal text with `strtol(..., 8)`, then calls `FileSystem::SetPermission()`.

## Control Flow
Options parse `-R`, permissions, and file. Recursive execution calls `Find()` and issues async `SetPermission` per result, using `PermissionState` to join callbacks. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
Runtime state includes parsed `uint16_t` permissions, a promise-backed completion handler, request counter, first error, find done flag, and mutex. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Permission parsing accepts octal conversion into `uint16_t`; oversized values can truncate after passing the `long` conversion. Recursive callback ordering must keep request counters balanced. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.h

## Purpose
Declares `Chmod`, the `HdfsTool` implementation for `hdfs-chmod`. implements `hdfs_chmod`, setting octal permissions for one path or a recursive listing.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `Chmod` derives from `HdfsTool`; `HandlePath(permissions, recursive, file)` validates octal text with `strtol(..., 8)`, then calls `FileSystem::SetPermission()`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. Runtime state includes parsed `uint16_t` permissions, a promise-backed completion handler, request counter, first error, find done flag, and mutex.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Permission parsing accepts octal conversion into `uint16_t`; oversized values can truncate after passing the `long` conversion. Recursive callback ordering must keep request counters balanced.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/main.cc

## Purpose
Provides the executable entry point for `hdfs-chmod`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Chmod`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/CMakeLists.txt

## Purpose
Builds the `hdfs-chown` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_chown_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> $<TARGET_OBJECTS:hdfs_ownership_obj> hdfs-chown.cc)`, `target_include_directories(hdfs_chown_lib PRIVATE ../../tools ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_chown_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_chown main.cc)`, `target_include_directories(hdfs_chown PRIVATE ../../tools)`, `target_link_libraries(hdfs_chown PRIVATE hdfs_chown_lib)`, `install(TARGETS hdfs_chown RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.cc

## Purpose
Implements `hdfs_chown`, changing owner and optionally group for one path or recursively.

## Important APIs, Types, And Functions
The implementation defines `Chown::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Chown` derives from `HdfsTool`; it parses `[OWNER][:[GROUP]]` via `Ownership` and calls `FileSystem::SetOwner()`.

## Control Flow
Options parse `-R`, user-group, and file. Non-recursive mode sends one async owner change. Recursive mode walks `Find()` results and fans out `SetOwner()` calls until all callbacks finish. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
Runtime state is held in shared `OwnerState`. Durable state changes are HDFS metadata owner/group updates. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Correct semantics depend on `Ownership` parsing empty owner/group correctly. Recursive first-error handling and request counter synchronization are the main concurrency risks. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.h

## Purpose
Declares `Chown`, the `HdfsTool` implementation for `hdfs-chown`. implements `hdfs_chown`, changing owner and optionally group for one path or recursively.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `Chown` derives from `HdfsTool`; it parses `[OWNER][:[GROUP]]` via `Ownership` and calls `FileSystem::SetOwner()`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. Runtime state is held in shared `OwnerState`. Durable state changes are HDFS metadata owner/group updates.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Correct semantics depend on `Ownership` parsing empty owner/group correctly. Recursive first-error handling and request counter synchronization are the main concurrency risks.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/hdfs-chown.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/main.cc

## Purpose
Provides the executable entry point for `hdfs-chown`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Chown`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chown/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/CMakeLists.txt

## Purpose
Builds the `hdfs-copy-to-local` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_copyToLocal_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> hdfs-copy-to-local.cc)`, `target_include_directories(hdfs_copyToLocal_lib PRIVATE ../../tools hdfs-copyToLocal ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_copyToLocal_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_copyToLocal main.cc)`, `target_include_directories(hdfs_copyToLocal PRIVATE ../../tools)`, `target_link_libraries(hdfs_copyToLocal PRIVATE hdfs_copyToLocal_lib)`, `install(TARGETS hdfs_copyToLocal RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.cc

## Purpose
Implements `hdfs_copytolocal`, copying one hdfs file into a local filesystem file.

## Important APIs, Types, And Functions
The implementation defines `CopyToLocal::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `CopyToLocal` derives from `HdfsTool`; `HandlePath(source, target)` opens `target` with `fopen(..., "wb")` and calls `readFile()`.

## Control Flow
The command validates exactly source and destination unless `-h` is used. It connects to HDFS, opens the destination, streams bytes, then closes the local file. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
Persistent side effect is local file creation/overwrite. HDFS is read-only. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Destination open errors are handled, but read/write errors rely on `readFile()` diagnostics and the function returns true after calling it. Local close errors are not checked. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.h

## Purpose
Declares `CopyToLocal`, the `HdfsTool` implementation for `hdfs-copy-to-local`. implements `hdfs_copyToLocal`, copying one HDFS file into a local filesystem file.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `CopyToLocal` derives from `HdfsTool`; `HandlePath(source, target)` opens `target` with `fopen(..., "wb")` and calls `readFile()`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. Persistent side effect is local file creation/overwrite. HDFS is read-only.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Destination open errors are handled, but read/write errors rely on `readFile()` diagnostics and the function returns true after calling it. Local close errors are not checked.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/hdfs-copy-to-local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/main.cc

## Purpose
Provides the executable entry point for `hdfs-copy-to-local`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::CopyToLocal`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-copy-to-local/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/CMakeLists.txt

## Purpose
Builds the `hdfs-count` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_count_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> hdfs-count.cc)`, `target_include_directories(hdfs_count_lib PRIVATE ../../tools hdfs-count ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_count_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_count main.cc)`, `target_include_directories(hdfs_count PRIVATE ../../tools)`, `target_link_libraries(hdfs_count PRIVATE hdfs_count_lib)`, `install(TARGETS hdfs_count RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc

## Purpose
Implements `hdfs_count`, printing hdfs content summary counts and optional quota columns.

## Important APIs, Types, And Functions
The implementation defines `Count::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Count` derives from `HdfsTool`; `HandlePath(show_quota, path)` calls synchronous `FileSystem::GetContentSummary()` and prints `ContentSummary::str(show_quota)`.

## Control Flow
Options parse `-q`, `-h`, and one path. Execution connects, fetches content summary, prints one line, or reports status failure. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
No persistent state. HDFS metadata is read-only. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Validation only requires at least one argument, so incompatible option combinations are delegated to program_options. Output formatting depends on `ContentSummary`. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.h

## Purpose
Declares `Count`, the `HdfsTool` implementation for `hdfs-count`. implements `hdfs_count`, printing HDFS content summary counts and optional quota columns.

## Important APIs, Types, And Functions
The class derives from `HdfsTool` and declares constructor, rule-of-five operations, `GetDescription()`, `Do()`, protected `Initialize()`, `ValidateConstraints()`, `HandleHelp()`, and the command-specific handler hook. `Count` derives from `HdfsTool`; `HandlePath(show_quota, path)` calls synchronous `FileSystem::GetContentSummary()` and prints `ContentSummary::str(show_quota)`.

## Control Flow
The inherited command pattern is parse in `Initialize()`, validate in `ValidateConstraints()`, and dispatch from `Do()` to help or the command handler. Tests override the protected handler from mock subclasses to verify parser dispatch.

## State And Persistence
Instance state is mostly inherited parser state plus a `po::positional_options_description`. No persistent state. HDFS metadata is read-only.

## Dependencies And Integration Points
Depends on Boost program_options and `hdfs-tool.h`; the implementation uses `tools_common` and libhdfs++ `FileSystem` APIs.

## Risks
Header and implementation signatures must stay aligned with gmock subclasses. Validation only requires at least one argument, so incompatible option combinations are delegated to program_options. Output formatting depends on `ContentSummary`.

## Test Signals
Signals include parser/mock tests for help and valid arguments plus integration tests against a real or mocked `FileSystem` for the handler behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/main.cc

## Purpose
Provides the executable entry point for `hdfs-count`.

## Important APIs, Types, And Functions
`main(int argc, char *argv[])` registers an `atexit` cleanup that calls `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Count`, invokes `Do()`, catches `std::exception`, and exits with failure on unsuccessful execution.

## Control Flow
Process startup schedules protobuf cleanup, creates the command object with raw CLI arguments, runs command parsing and action through `Do()`, prints caught exception messages to stderr, and maps the boolean result to process exit status.

## State And Persistence
No persistent state in the entry point. It coordinates process lifecycle and protobuf static cleanup.

## Dependencies And Integration Points
Depends on the command header and protobuf runtime cleanup API. It is linked by the command-specific CMake target.

## Risks
If `atexit` registration fails, the process exits immediately. All command errors are collapsed into `EXIT_FAILURE`, so callers need stderr for detail.

## Test Signals
Executable-level tests should verify help success, bad argument failure, thrown exception reporting, and no protobuf leak reports under sanitizers or valgrind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/CMakeLists.txt

## Purpose
Builds the `hdfs-create-snapshot` libhdfs++ command-line tool library and executable.

## Important APIs, Types, And Functions
CMake declarations: `add_library(hdfs_createSnapshot_lib STATIC $<TARGET_OBJECTS:hdfs_tool_obj> hdfs-create-snapshot.cc)`, `target_include_directories(hdfs_createSnapshot_lib PRIVATE ../../tools ${Boost_INCLUDE_DIRS})`, `target_link_libraries(hdfs_createSnapshot_lib PRIVATE Boost::boost Boost::program_options tools_common hdfspp_static)`, `add_executable(hdfs_createSnapshot main.cc)`, `target_include_directories(hdfs_createSnapshot PRIVATE ../../tools)`, `target_link_libraries(hdfs_createSnapshot PRIVATE hdfs_createSnapshot_lib)`, `install(TARGETS hdfs_createSnapshot RUNTIME DESTINATION bin)`.

## Control Flow
CMake creates a static tool-specific library from the shared `hdfs_tool_obj` object and the command implementation source, wires include directories and dependencies, then builds and installs the executable from `main.cc`.

## State And Persistence
No runtime state. Build artifacts are the static library and installed executable.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common`, `hdfspp_static`, and shared command base object code. The top-level tools CMake file adds this directory.

## Risks
Target naming follows Hadoop's historical camel-case executable names for some commands; renames can break tests and install scripts. Missing include paths or link dependencies surface at build time.

## Test Signals
Successful CMake generation, compilation, and install target creation validate this build glue.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/CMakeLists.txt -->
