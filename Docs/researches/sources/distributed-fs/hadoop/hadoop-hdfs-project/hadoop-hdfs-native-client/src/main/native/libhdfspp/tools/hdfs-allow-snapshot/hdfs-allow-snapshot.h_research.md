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
