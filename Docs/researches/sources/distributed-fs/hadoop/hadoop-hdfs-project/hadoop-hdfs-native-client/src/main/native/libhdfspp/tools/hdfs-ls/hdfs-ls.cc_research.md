<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.cc` implements `hdfs_ls`, which lists `StatInfo` rows for a path, optionally recursively. The source was read as a complete 156-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and listing callback. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH` plus `-R`, uses `GetListing` for shallow output or `Find` for recursive output, prints each `StatInfo::str()`, and waits on a promise.

## State and Persistence Behavior

read-only; only callback status and promise state persist for the command lifetime. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: large recursive listings, callback termination assumptions, and formatting compatibility with expected CLI output. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call. Include large-directory and multi-callback tests because the implementation relies on async callback completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.cc -->
