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
