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
