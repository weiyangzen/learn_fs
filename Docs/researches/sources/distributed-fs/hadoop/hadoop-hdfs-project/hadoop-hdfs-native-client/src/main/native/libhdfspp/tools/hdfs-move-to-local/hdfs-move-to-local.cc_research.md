<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.cc` implements `hdfs_moveToLocal`, which copies one HDFS file to a local path and deletes the source after successful read completion. The source was read as a complete 135-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `ValidateConstraints`, `Do`, `HandlePath`, and shared `readFile`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: requires `SRC_FILE DST_FILE`, opens the local destination with `fopen(..., "wb")`, streams HDFS data through `readFile`, and passes `to_delete=true` to remove the source after EOF.

## State and Persistence Behavior

persists a local file and deletes HDFS source state only after readFile reaches end-of-file. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: partial local files after read failures, local overwrite behavior, non-atomic move semantics, and process exits inside shared read helper. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.cc -->
