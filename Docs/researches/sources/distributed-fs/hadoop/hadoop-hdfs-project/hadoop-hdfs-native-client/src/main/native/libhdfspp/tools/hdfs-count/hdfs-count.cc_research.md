<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc

## Purpose
Implements `hdfs_count`, printing hdfs content summary counts and optional quota columns.

## Important APIs, Types, And Functions
The implementation defines `Count::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Count` derives from `HdfsTool`; `HandlePath(show_quota, path)` calls synchronous `FileSystem::GetContentSummary()` and prints `ContentSummary::str(show_quota)`.

## Control Flow
Options parse `-q`, `-h`, and one path. Execution connects, fetches content summary, prints one line, or reports status failure. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
No persistent state. HDFS metadata is read-only. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Validation only requires at least one argument, so incompatible option combinations are delegated to program_options. Output formatting depends on `ContentSummary`. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-count/hdfs-count.cc -->
