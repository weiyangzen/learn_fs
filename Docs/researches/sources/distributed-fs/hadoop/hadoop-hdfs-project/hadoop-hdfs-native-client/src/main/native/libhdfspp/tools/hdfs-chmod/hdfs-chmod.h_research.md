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
