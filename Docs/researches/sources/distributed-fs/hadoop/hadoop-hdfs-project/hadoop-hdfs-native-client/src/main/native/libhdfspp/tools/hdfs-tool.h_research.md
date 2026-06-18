<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.h` declares `hdfs::tools::HdfsTool`, the abstract base class for libhdfs++ native command-line tools. The source was read as a complete 113-line file for this report.

## Important APIs, Types, and Functions

`HdfsTool` stores `argc_`, `argv_`, `po::variables_map opt_val_`, and `po::options_description opt_desc_`. It requires derived classes to implement `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. Copy/move construction is defaulted, while assignment is deleted, and the virtual destructor is declared out-of-line.

## Control Flow

The base class defines the lifecycle contract but does not run it. Each command's `main.cc` constructs a derived class and calls `Do()`, while derived `Do()` implementations call parsing, validation, help handling, and operation dispatch.

## State and Persistence Behavior

All state is process-local command parser state. HDFS or local filesystem persistence is owned by derived command handlers.

## Dependencies and Integration Points

This header centralizes Boost Program Options integration and provides the polymorphic interface used by every native command library and executable wrapper.

## Risks and Edge Cases

Changing virtual signatures breaks all tools. Since validation is left to each command, inconsistent argument semantics can appear across commands even though they share the base.

## Test Signals

Build all native tools, run help/invalid-argument smoke tests for each derived class, and compile any test doubles that override the protected lifecycle methods.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.h -->
