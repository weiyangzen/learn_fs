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
