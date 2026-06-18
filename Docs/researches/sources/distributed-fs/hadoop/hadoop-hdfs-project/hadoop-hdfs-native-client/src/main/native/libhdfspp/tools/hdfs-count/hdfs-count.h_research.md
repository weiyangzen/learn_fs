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
