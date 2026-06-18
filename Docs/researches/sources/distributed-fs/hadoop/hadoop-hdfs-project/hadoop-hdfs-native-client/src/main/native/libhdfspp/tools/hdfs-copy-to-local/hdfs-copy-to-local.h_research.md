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
