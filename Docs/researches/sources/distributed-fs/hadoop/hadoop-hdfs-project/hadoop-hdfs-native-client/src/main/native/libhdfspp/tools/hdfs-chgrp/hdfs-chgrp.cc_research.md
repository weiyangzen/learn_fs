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
