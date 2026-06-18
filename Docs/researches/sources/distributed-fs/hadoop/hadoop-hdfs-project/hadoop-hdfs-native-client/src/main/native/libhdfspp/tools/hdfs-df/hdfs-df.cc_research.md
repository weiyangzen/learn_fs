<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.cc` implements `hdfs_df`, which prints capacity, used, and remaining filesystem space for the cluster containing `PATH`. The source was read as a complete 113-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses one path, connects to the URI or default FS, calls `GetFsStats`, then prints `FsInfo::str("hdfs://" + fs->get_cluster_name())`.

## State and Persistence Behavior

read-only metadata operation with no persistence beyond stdout. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: path is used mainly for connection selection, so multi-cluster URI handling and defaultFS configuration are the main edge cases. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.cc -->
