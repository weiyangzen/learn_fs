<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc

## Purpose
Implements `hdfs_chmod`, setting octal permissions for one path or a recursive listing.

## Important APIs, Types, And Functions
The implementation defines `Chmod::Initialize()`, `GetDescription()`, `Do()`, `HandleHelp()`, and the command-specific handler. `Chmod` derives from `HdfsTool`; `HandlePath(permissions, recursive, file)` validates octal text with `strtol(..., 8)`, then calls `FileSystem::SetPermission()`.

## Control Flow
Options parse `-R`, permissions, and file. Recursive execution calls `Find()` and issues async `SetPermission` per result, using `PermissionState` to join callbacks. On failure paths it prints usage or status details and returns false so `main.cc` can exit with failure.

## State And Persistence
Runtime state includes parsed `uint16_t` permissions, a promise-backed completion handler, request counter, first error, find done flag, and mutex. Parser state lives in `opt_desc_`, `pos_opt_desc_`, and `opt_val_` for one command invocation.

## Dependencies And Integration Points
Depends on Boost program_options, `tools_common` helpers such as `parse_path_or_exit()`, `doConnect()`, and for stream-copying commands `readFile()`. It integrates with libhdfs++ `FileSystem` APIs and the command-specific executable entry point.

## Risks
Permission parsing accepts octal conversion into `uint16_t`; oversized values can truncate after passing the `long` conversion. Recursive callback ordering must keep request counters balanced. The parser-dispatch surface is covered by mock tests, but real HDFS status and I/O behavior require integration coverage.

## Test Signals
Useful signals are successful help output, correct rejection of bad arity/options, expected handler dispatch in `hdfs-tool-tests.cc`, and integration success/failure against HDFS for the underlying FileSystem call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-chmod/hdfs-chmod.cc -->
