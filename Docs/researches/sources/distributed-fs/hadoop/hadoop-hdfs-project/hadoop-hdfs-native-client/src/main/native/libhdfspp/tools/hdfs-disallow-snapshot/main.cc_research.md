<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/main.cc` is the standalone process entry point for `hdfs_disallowSnapshot`. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::DisallowSnapshot`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `DisallowSnapshot::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_disallowSnapshot` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_disallowSnapshot --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `DisallowSnapshot::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/main.cc -->
