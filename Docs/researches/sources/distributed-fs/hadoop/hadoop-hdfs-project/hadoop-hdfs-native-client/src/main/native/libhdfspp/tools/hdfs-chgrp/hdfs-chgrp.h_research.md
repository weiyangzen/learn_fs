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
