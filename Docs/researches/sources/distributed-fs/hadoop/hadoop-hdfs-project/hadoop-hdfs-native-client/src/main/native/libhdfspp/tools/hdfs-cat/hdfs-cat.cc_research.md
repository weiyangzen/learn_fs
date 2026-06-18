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
