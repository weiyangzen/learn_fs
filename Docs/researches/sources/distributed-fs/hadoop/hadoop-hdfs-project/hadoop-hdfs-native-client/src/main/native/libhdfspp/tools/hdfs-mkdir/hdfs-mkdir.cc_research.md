<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.cc` implements `hdfs_mkdir`, which creates directories with optional parent creation and optional octal mode. The source was read as a complete 140-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and static `GetPermissions`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH`, `-p`, and `-m`, converts permissions with `std::strtol(..., 8)`, then calls `FileSystem::Mkdirs(path, mode, create_parents)`.

## State and Persistence Behavior

NameNode persists directory creation and permission bits; local option state is transient. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: `strtol` errors are not checked, invalid octal strings can silently become unintended permissions, and default permission masking lives in libhdfs++. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call. Include malformed numeric input tests because `std::strtol` errors are not checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.cc -->
