<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.cc` implements `hdfs_deleteSnapshot`, which deletes a named snapshot from a snapshot-able directory. The source was read as a complete 133-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `ValidateConstraints`, `Do`, `HandleSnapshot`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: requires `PATH NAME`, connects through `doConnect`, then calls `FileSystem::DeleteSnapshot(uri.get_path(), name)`.

## State and Persistence Behavior

snapshot namespace changes are persisted by the NameNode; local state is just parsed arguments. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: requires exactly enough arguments, depends on snapshot owner privilege, and returns NameNode errors directly. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.cc -->
