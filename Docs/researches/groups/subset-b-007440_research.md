# subset-b-007440 Research

Grouped source research for libhdfs++ native HDFS command tools and the Hadoop HDFS NFS gateway files in subset-b-007440. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.cc` implements `hdfs_createSnapshot`, which creates a snapshot for a snapshot-enabled directory, optionally using `-n` for an explicit name. The source was read as a complete 138-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `ValidateConstraints`, `Do`, `HandleSnapshot`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH` and optional `--name`, connects through `doConnect`, then calls `FileSystem::CreateSnapshot(uri.get_path(), name.value_or(""))`.

## State and Persistence Behavior

snapshot metadata is persisted by the NameNode; this process owns only transient option state. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: argument counting around optional `-n`, empty-name defaulting, owner privilege failures, and URI parsing failures. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.h` declares the `hdfs::tools::CreateSnapshot` command class for `hdfs_createSnapshot`, which creates a snapshot for a snapshot-enabled directory, optionally using `-n` for an explicit name. The source was read as a complete 96-line file for this report.

## Important APIs, Types, and Functions

`CreateSnapshot` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/hdfs-create-snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/main.cc` is the standalone process entry point for `hdfs_createSnapshot`. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::CreateSnapshot`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `CreateSnapshot::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_createSnapshot` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_createSnapshot --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `CreateSnapshot::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-create-snapshot/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_deleteSnapshot` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_deleteSnapshot` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_deleteSnapshot`, install-layout checks for `bin/hdfs_deleteSnapshot`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.h` declares the `hdfs::tools::DeleteSnapshot` command class for `hdfs_deleteSnapshot`, which deletes a named snapshot from a snapshot-able directory. The source was read as a complete 93-line file for this report.

## Important APIs, Types, and Functions

`DeleteSnapshot` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/hdfs-delete-snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/main.cc` is the standalone process entry point for `hdfs_deleteSnapshot`. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::DeleteSnapshot`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `DeleteSnapshot::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_deleteSnapshot` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_deleteSnapshot --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `DeleteSnapshot::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-delete-snapshot/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_df` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_df` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_df`, install-layout checks for `bin/hdfs_df`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.h` declares the `hdfs::tools::Df` command class for `hdfs_df`, which prints capacity, used, and remaining filesystem space for the cluster containing `PATH`. The source was read as a complete 90-line file for this report.

## Important APIs, Types, and Functions

`Df` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/hdfs-df.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/main.cc` is the standalone process entry point for `hdfs_df`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Df`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Df::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_df` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_df --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Df::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-df/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_disallowSnapshot` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_disallowSnapshot` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_disallowSnapshot`, install-layout checks for `bin/hdfs_disallowSnapshot`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.cc` implements `hdfs_disallowSnapshot`, which marks a directory as no longer snapshot-able after existing snapshots have been removed. The source was read as a complete 117-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandleSnapshot`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH`, connects, and calls `FileSystem::DisallowSnapshot(uri.get_path())`.

## State and Persistence Behavior

directory snapshottable state is persisted by the NameNode. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: fails when snapshots remain, permissions are insufficient, or argument validation allows help-like extra input. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.h` declares the `hdfs::tools::DisallowSnapshot` command class for `hdfs_disallowSnapshot`, which marks a directory as no longer snapshot-able after existing snapshots have been removed. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

`DisallowSnapshot` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-disallow-snapshot/hdfs-disallow-snapshot.h -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_du` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_du` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_du`, install-layout checks for `bin/hdfs_du`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.cc` implements `hdfs_du`, which computes content-summary output for a file or for directory children, optionally recursively. The source was read as a complete 205-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, async `GetListing`/`Find` callback, and async `GetContentSummary` callback. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: creates a promise, scans with `GetListing` or `Find`, launches one `GetContentSummary` per returned `StatInfo`, tracks request count in `GetContentSummaryState`, then prints `ContentSummary::str_du()`.

## State and Persistence Behavior

read-only namespace/content-summary operation; shared in-process state is a mutex, status, request counter, and find completion flag. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: unbounded async fan-out on large trees, callback ordering races if state locking changes, and first-error-only status reporting. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call. Include large-directory and multi-callback tests because the implementation relies on async callback completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.h` declares the `hdfs::tools::Du` command class for `hdfs_du`, which computes content-summary output for a file or for directory children, optionally recursively. The source was read as a complete 93-line file for this report.

## Important APIs, Types, and Functions

`Du` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/hdfs-du.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/main.cc` is the standalone process entry point for `hdfs_du`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Du`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Du::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_du` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_du --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Du::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-du/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_find` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_find` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_find`, install-layout checks for `bin/hdfs_find`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.cc` implements `hdfs_find`, which recursively lists paths matching an optional name glob and maximum depth. The source was read as a complete 194-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and the `Find` result callback. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH`, `--name`, and `--max-depth`, connects with extended timeout, calls `FileSystem::Find`, prints each `StatInfo::str()`, and fulfills a promise when `has_more_results` becomes false.

## State and Persistence Behavior

read-only; all state is the promise plus final status captured by the callback. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: max-depth zero semantics, wildcard matching, default maximum depth, and callback guarantee assumptions. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call. Include large-directory and multi-callback tests because the implementation relies on async callback completion semantics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.h` declares the `hdfs::tools::Find` command class for `hdfs_find`, which recursively lists paths matching an optional name glob and maximum depth. The source was read as a complete 96-line file for this report.

## Important APIs, Types, and Functions

`Find` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/hdfs-find.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/main.cc` is the standalone process entry point for `hdfs_find`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Find`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Find::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_find` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_find --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Find::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-find/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_get` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_get` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`. `hdfs_get_lib` additionally links `hdfs_copyToLocal_lib`, because the `Get` implementation is only a subclass of the copy-to-local command.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_get`, install-layout checks for `bin/hdfs_get`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.cc` implements the thin `hdfs::tools::Get` adapter for the native `hdfs_get` command. The source was read as a complete 25-line file for this report.

## Important APIs, Types, and Functions

The implementation contains `Get::Get(int, char **)`, which delegates construction to `CopyToLocal`, and `Get::GetToolName()`, which returns the command name string `get`.

## Control Flow

All argument parsing, validation, connection setup, local destination opening, and file streaming are inherited from `CopyToLocal`. This file only changes the displayed/tool identity used by the base behavior.

## State and Persistence Behavior

No state is introduced here. The inherited base may create a local file and read from HDFS, but this adapter itself is stateless after construction.

## Dependencies and Integration Points

It includes `hdfs-get.h`, which depends on the copy-to-local command header. The CMake target must link `hdfs_copyToLocal_lib` in addition to the common libhdfs++ tool dependencies.

## Risks and Edge Cases

The main risk is behavioral drift in `CopyToLocal`: `get` has no implementation of its own to compensate. Tests should verify that help text and error text name the correct tool after the override.

## Test Signals

Build `hdfs_get`, run `hdfs_get --help`, and exercise one successful HDFS-to-local copy through the `get` executable to ensure the inherited flow is correctly wired.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.h` declares the `hdfs::tools::Get` command class for `hdfs_get`, which provides a `get` command alias over `CopyToLocal` behavior. The source was read as a complete 47-line file for this report.

## Important APIs, Types, and Functions

`Get` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing. This header is intentionally thin: `Get` inherits `CopyToLocal` and exposes only construction plus the protected `GetToolName()` override.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/hdfs-get.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/main.cc` is the standalone process entry point for `hdfs_get`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Get`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Get::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_get` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_get --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Get::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-get/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_ls` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_ls` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_ls`, install-layout checks for `bin/hdfs_ls`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.h` declares the `hdfs::tools::Ls` command class for `hdfs_ls`, which lists `StatInfo` rows for a path, optionally recursively. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

`Ls` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/hdfs-ls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/main.cc` is the standalone process entry point for `hdfs_ls`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Ls`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Ls::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_ls` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_ls --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Ls::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-ls/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_mkdir` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_mkdir` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_mkdir`, install-layout checks for `bin/hdfs_mkdir`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.h` declares the `hdfs::tools::Mkdir` command class for `hdfs_mkdir`, which creates directories with optional parent creation and optional octal mode. The source was read as a complete 105-line file for this report.

## Important APIs, Types, and Functions

`Mkdir` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing. The header exposes `GetPermissions()` as a static helper so tests can verify octal parsing independent of command execution.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/hdfs-mkdir.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/main.cc` is the standalone process entry point for `hdfs_mkdir`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Mkdir`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Mkdir::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_mkdir` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_mkdir --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Mkdir::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-mkdir/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_moveToLocal` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_moveToLocal` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_moveToLocal`, install-layout checks for `bin/hdfs_moveToLocal`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/CMakeLists.txt -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.h` declares the `hdfs::tools::MoveToLocal` command class for `hdfs_moveToLocal`, which copies one HDFS file to a local path and deletes the source after successful read completion. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

`MoveToLocal` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/hdfs-move-to-local.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/main.cc` is the standalone process entry point for `hdfs_moveToLocal`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::MoveToLocal`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `MoveToLocal::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_moveToLocal` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_moveToLocal --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `MoveToLocal::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-move-to-local/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_renameSnapshot` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_renameSnapshot` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_renameSnapshot`, install-layout checks for `bin/hdfs_renameSnapshot`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.cc` implements `hdfs_renameSnapshot`, which renames an existing snapshot under a snapshot-able directory. The source was read as a complete 139-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `ValidateConstraints`, `Do`, and `HandleSnapshot`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: requires `PATH OLD_NAME NEW_NAME`, connects through `doConnect`, and calls `FileSystem::RenameSnapshot(uri.get_path(), old_name, new_name)`.

## State and Persistence Behavior

snapshot name metadata is persisted by the NameNode. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: argument counting, owner privileges, name collisions, and invalid snapshot names are delegated to the NameNode. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.h` declares the `hdfs::tools::RenameSnapshot` command class for `hdfs_renameSnapshot`, which renames an existing snapshot under a snapshot-able directory. The source was read as a complete 95-line file for this report.

## Important APIs, Types, and Functions

`RenameSnapshot` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/hdfs-rename-snapshot.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/main.cc` is the standalone process entry point for `hdfs_renameSnapshot`. The source was read as a complete 54-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::RenameSnapshot`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `RenameSnapshot::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_renameSnapshot` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_renameSnapshot --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `RenameSnapshot::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rename-snapshot/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_rm` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_rm` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_rm`, install-layout checks for `bin/hdfs_rm`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.cc` implements `hdfs_rm`, which removes a file or directory with optional recursive deletion. The source was read as a complete 114-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses `PATH` and `-R`, connects, then calls `FileSystem::Delete(uri.get_path(), recursive)`.

## State and Persistence Behavior

namespace mutation is persisted by the NameNode; command state is transient. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: recursive flag correctness, accidental directory deletion, snapshot/trash semantics outside this native wrapper, and URI parse failures. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.h` declares the `hdfs::tools::Rm` command class for `hdfs_rm`, which removes a file or directory with optional recursive deletion. The source was read as a complete 92-line file for this report.

## Important APIs, Types, and Functions

`Rm` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/hdfs-rm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/main.cc` is the standalone process entry point for `hdfs_rm`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Rm`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Rm::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_rm` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_rm --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Rm::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-rm/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_setrep` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_setrep` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_setrep`, install-layout checks for `bin/hdfs_setrep`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.cc` implements `hdfs_setrep`, which changes replication for a file or all files under a directory tree. The source was read as a complete 220-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `ValidateConstraints`, `Do`, `HandlePath`, `SetReplicationState`, `Find`, and async `SetReplication` callbacks. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses replication and path, converts replication with `std::strtol(..., 8)`, uses recursive `Find`, calls `SetReplication` for file entries only, and waits until find is done and all requests finish.

## State and Persistence Behavior

replication changes are persisted by HDFS block management; in-process state tracks replication, request count, status, and completion. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: replication parsing uses base 8, callback fan-out can be large, directories are skipped intentionally, and first failure wins. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call. Include large-directory and multi-callback tests because the implementation relies on async callback completion semantics. Include malformed numeric input tests because `std::strtol` errors are not checked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.h` declares the `hdfs::tools::Setrep` command class for `hdfs_setrep`, which changes replication for a file or all files under a directory tree. The source was read as a complete 96-line file for this report.

## Important APIs, Types, and Functions

`Setrep` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/hdfs-setrep.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/main.cc` is the standalone process entry point for `hdfs_setrep`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Setrep`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Setrep::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_setrep` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_setrep --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Setrep::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-setrep/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_stat` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_stat` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_stat`, install-layout checks for `bin/hdfs_stat`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.cc` implements `hdfs_stat`, which prints file or directory metadata for one path. The source was read as a complete 111-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, and `GetDescription`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: parses one path, connects, calls `GetFileInfo`, and prints `StatInfo::str()`.

## State and Persistence Behavior

read-only metadata fetch with no persistence beyond stdout. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: missing paths, URI parsing, and format compatibility are the primary concerns. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.h` declares the `hdfs::tools::Stat` command class for `hdfs_stat`, which prints file or directory metadata for one path. The source was read as a complete 90-line file for this report.

## Important APIs, Types, and Functions

`Stat` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/hdfs-stat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/main.cc` is the standalone process entry point for `hdfs_stat`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Stat`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Stat::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_stat` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_stat --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Stat::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-stat/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/CMakeLists.txt` is the CMake wiring for the libhdfs++ `hdfs_tail` command. The source was read as a complete 27-line file for this report.

## Important APIs, Types, and Functions

The file defines a static command library, adds `$<TARGET_OBJECTS:hdfs_tool_obj>` plus the command implementation source, sets private include directories for `../../tools` and Boost, links Boost, `Boost::program_options`, `tools_common`, and `hdfspp_static`, creates the `hdfs_tail` executable from `main.cc`, links it to the command library, and installs the runtime into `bin`.

## Control Flow

There is no runtime control flow. At configure and build time this file makes the command implementation reusable as a library and then builds the standalone executable wrapper.

## State and Persistence Behavior

Build state is confined to CMake targets and generated build-system metadata. Runtime persistence is controlled by the corresponding command implementation, not by this file.

## Dependencies and Integration Points

The target integrates the common `HdfsTool` object, Boost Program Options parsing, shared `tools_common` connection helpers, and static libhdfs++ client library. The installed executable becomes part of the native HDFS CLI tool set.

## Risks and Edge Cases

Incorrect target dependencies surface as link failures or as executables missing shared helper symbols. Include-directory drift can also hide accidental dependence on sibling command headers.

## Test Signals

Useful signals are CMake configure success, native-client build success for `hdfs_tail`, install-layout checks for `bin/hdfs_tail`, and smoke execution of `--help` to prove the executable links and starts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.cc` implements `hdfs_tail`, which prints the last 1024 bytes of a file and optionally follows growth. The source was read as a complete 150-line file for this report.

## Important APIs, Types, and Functions

Important members are `Initialize`, `Do`, `HandlePath`, `tail_size_in_bytes`, and `refresh_rate_in_sec`. The implementation uses Boost Program Options for command-line parsing, `hdfs::parse_path_or_exit` for URI handling, `hdfs::doConnect` for libhdfs++ connection setup, and command-specific `hdfs::FileSystem` APIs for the actual operation.

## Control Flow

`Do()` calls `Initialize()`, rejects invalid constraints by printing `GetDescription()`, handles `--help`, extracts parsed options, and then dispatches to the command handler. The core operation flow is: stats the file, starts at `length - 1024` when needed, calls shared `readFile`, and when `-f` is set polls `GetFileInfo` every second until the length increases.

## State and Persistence Behavior

read-only against HDFS; local state tracks current offset and stat info during a possibly long-running process. The command object stores only parsed command-line data and transient callback/promise state where asynchronous APIs are used.

## Dependencies and Integration Points

This file integrates the command with `hdfs-tool.h`, `tools_common`, libhdfs++ `FileSystem`, Boost Program Options, and standard I/O diagnostics. It is packaged by the sibling CMake target and reached from `main.cc`.

## Risks and Edge Cases

Primary risks: file truncation/rotation is not handled, polling uses size only, and shared `readFile` exits the process on non-EOF errors. Errors are mostly surfaced as `Status::ToString()` on stderr, while malformed URI handling exits in the shared helper.

## Test Signals

Use `--help`, missing/extra argument tests, URI parse failures, a MiniDFSCluster-backed success path, and failure injection for the underlying `FileSystem` call.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.h` declares the `hdfs::tools::Tail` command class for `hdfs_tail`, which prints the last 1024 bytes of a file and optionally follows growth. The source was read as a complete 102-line file for this report.

## Important APIs, Types, and Functions

`Tail` derives from `HdfsTool`, follows the local Rule-of-5 convention, deletes assignment, and overrides `GetDescription()`, `Do()`, `Initialize()`, `ValidateConstraints()`, and `HandleHelp()`. The command-specific protected handler is the main test seam for invoking the HDFS operation after parsing. The header also defines the 1024-byte tail window and one-second follow refresh interval as compile-time constants.

## Control Flow

The header has no executable flow, but it defines the contract used by `main.cc`: construct the command with `argc/argv`, call `Do()`, and let the implementation parse options before dispatching to its handler.

## State and Persistence Behavior

State declared here is command-lifetime parser state: inherited `argc_`, `argv_`, option map/description, plus a private `po::positional_options_description`. Durable state changes happen only through the implementation's libhdfs++ calls.

## Dependencies and Integration Points

The declaration integrates Boost Program Options with the shared `HdfsTool` base and is consumed by the sibling implementation, test subclasses, and executable wrapper.

## Risks and Edge Cases

Header changes can break command ABI expectations across tests and CMake targets. The validation contract is intentionally small, so parser semantics and exact argument counts need implementation-level coverage.

## Test Signals

Compile coverage of the command library, subclass tests for the protected handler where available, `--help` output checks, and invalid argument count tests are the strongest signals for this declaration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/hdfs-tail.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/main.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/main.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/main.cc` is the standalone process entry point for `hdfs_tail`. The source was read as a complete 52-line file for this report.

## Important APIs, Types, and Functions

The only function is `main(int argc, char *argv[])`. It registers a `std::atexit` cleanup callback for `google::protobuf::ShutdownProtobufLibrary()`, constructs `hdfs::tools::Tail`, calls `Do()`, catches `std::exception`, and exits with `EXIT_FAILURE` when the command reports failure.

## Control Flow

Startup first schedules protobuf cleanup, then delegates all command-specific parsing and HDFS operations to `Tail::Do()`. Exceptions are converted into stderr output and a false success flag, which maps to a non-zero process exit.

## State and Persistence Behavior

This file owns no durable state. Its only process-lifetime state is the command object and the protobuf cleanup registration. Any HDFS or local filesystem mutation is performed by the command implementation.

## Dependencies and Integration Points

It depends on the command header, the C runtime exit APIs, standard exception handling, iostream diagnostics, and protobuf static cleanup. It is linked by the sibling `CMakeLists.txt` into the installed `hdfs_tail` binary.

## Risks and Edge Cases

If `atexit` registration fails, the process exits before parsing arguments. Catching only `std::exception` leaves non-standard throws uncaught. Some copied wrappers have slightly inaccurate error text, but the exit behavior remains consistent.

## Test Signals

Run `hdfs_tail --help` and invalid-argument cases to verify process exit codes, stderr/stdout routing, and protobuf cleanup registration. Command-specific integration tests should exercise `Tail::Do()` through this wrapper at least once.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tail/main.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.cc` provides the out-of-line virtual destructor definition for `hdfs::tools::HdfsTool`. The source was read as a complete 26-line file for this report.

## Important APIs, Types, and Functions

The only definition is `hdfs::tools::HdfsTool::~HdfsTool() {}`. It anchors the vtable out of line instead of duplicating inline destructor definitions in every translation unit.

## Control Flow

There is no operational command flow here. Runtime control reaches this destructor through normal deletion/destruction of derived command objects.

## State and Persistence Behavior

No state is modified. Derived classes and their members clean up through standard C++ destruction.

## Dependencies and Integration Points

It includes `hdfs-tool.h` and is compiled into the shared `hdfs_tool_obj` object target consumed by command libraries.

## Risks and Edge Cases

If this object is omitted from a command library, link errors around the destructor or vtable can appear. Adding destructor logic here would affect every native tool.

## Test Signals

Native tool link success and clean destruction under sanitizer/valgrind runs validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/hdfs-tool.cc -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/CMakeLists.txt

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/CMakeLists.txt` builds the internal native helper object library for ownership parsing. The source was read as a complete 19-line file for this report.

## Important APIs, Types, and Functions

The single CMake command is `add_library(hdfs_ownership_obj OBJECT hdfs-ownership.cc)`, producing an object target that other command libraries can include without creating a standalone executable.

## Control Flow

There is no runtime control flow. Configure-time CMake registers the object target for later link composition.

## State and Persistence Behavior

Only build metadata is persisted in the generated build directory. Runtime ownership parsing state is implemented in `hdfs-ownership.cc/.h`.

## Dependencies and Integration Points

The object target supplies shared ownership parsing code to tools such as chown/chgrp and keeps it separate from executable-specific libraries.

## Risks and Edge Cases

If the object target is omitted from a dependent command, the build fails at link time. Since it is an object library, consumers must manage their own include directories and dependencies.

## Test Signals

CMake configure/build success for ownership-using tools and unit tests around `Ownership` construction and equality are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/CMakeLists.txt -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h` declares `GetContentSummaryState`, the shared callback state used by `hdfs_du` while it fans out asynchronous content-summary requests. The source was read as a complete 68-line file for this report.

## Important APIs, Types, and Functions

`GetContentSummaryState` stores a final status handler, `request_counter`, `find_is_done`, accumulated `hdfs::Status`, and a mutex. The constructor moves the handler and initializes the counter and find-completion flag.

## Control Flow

The struct itself has no flow. `hdfs-du.cc` increments `request_counter` for each `GetContentSummary` call, decrements it in callbacks, sets `find_is_done` when listing completes, and invokes `handler(status)` once both conditions are satisfied.

## State and Persistence Behavior

All state is in-memory and command-lifetime only. The mutex protects shared fields because content-summary callbacks can run concurrently.

## Dependencies and Integration Points

It depends on `<functional>`, `<mutex>`, and `hdfspp/hdfspp.h`, and is tightly coupled to the asynchronous `FileSystem::GetContentSummary` callback contract.

## Risks and Edge Cases

Incorrect counter updates can deadlock the command or complete before all results print. Maintaining the first failure while still draining callbacks is the key concurrency invariant.

## Test Signals

Recursive `du` tests with empty directories, many entries, injected `GetContentSummary` failures, and concurrent callback ordering are the strongest signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/get-content-summary-state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc` implements the `Ownership` parser and equality semantics for native ownership-changing tools. The source was read as a complete 44-line file for this report.

## Important APIs, Types, and Functions

`Ownership::Ownership(const std::string&)` splits on the first colon. Without a colon, the whole input is the user. With a colon, the prefix is `user_` and the suffix becomes optional `group_`. `operator==` compares users and requires both groups to be present and equal or both absent.

## Control Flow

Construction performs one `find(':')` and either stores the entire string as user or populates user/group substrings. Equality first checks user equality, then branches on group optionality.

## State and Persistence Behavior

The implementation persists no external state. It creates immutable parsed ownership values used later by command handlers.

## Dependencies and Integration Points

It includes `hdfs-ownership.h` and lives in `hdfs::tools`, feeding chown/chgrp command parsing and tests.

## Risks and Edge Cases

There is no validation for empty user or group components; `user:` produces an engaged empty group. Only the first colon is structural, so additional colons remain inside the group string.

## Test Signals

Focused parser/equality tests for no-colon, colon, empty components, multiple colons, and optional group equality cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h` declares shared ownership helper types for native HDFS ownership-changing commands. The source was read as a complete 88-line file for this report.

## Important APIs, Types, and Functions

`Ownership` parses a `user[:group]` string and exposes `GetUser()`, `GetGroup()`, and equality comparison. `OwnerState` stores username, group, callback handler, outstanding request counter, completion flag, final status, and mutex for recursive async owner updates.

## Control Flow

The header defines data contracts only. Implementations parse CLI ownership specifications into `Ownership`; recursive ownership commands use `OwnerState` similarly to the replication and content-summary state structs.

## State and Persistence Behavior

The parsed user/group and callback counters are transient in-memory state. Durable HDFS ownership changes are performed by the commands that consume these types.

## Dependencies and Integration Points

It depends on optional strings, function callbacks, mutexes, and `hdfspp/status.h`, and integrates with chown/chgrp-style command implementations.

## Risks and Edge Cases

Empty users, trailing colons, absent groups, and equality semantics between optional and non-optional groups are the main parser risks.

## Test Signals

Unit tests should cover `user`, `user:group`, `user:`, `:group`, equality with and without group values, and recursive callback completion behavior in ownership commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/hdfs-ownership.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h` declares `SetReplicationState`, the shared state used by `hdfs_setrep` while applying replication changes across a recursive listing. The source was read as a complete 72-line file for this report.

## Important APIs, Types, and Functions

`SetReplicationState` stores the target `replication`, a completion handler, `request_counter`, `find_is_done`, final `hdfs::Status`, and a mutex. The constructor initializes these values for the callback fan-out in `hdfs-setrep.cc`.

## Control Flow

The struct supports the flow where `Find` discovers files, each file schedules async `SetReplication`, and the final handler runs only after listing is complete and all outstanding replication calls have returned.

## State and Persistence Behavior

State is in-memory and lasts only for one command invocation. HDFS persists the replication factor changes; this struct only coordinates callback completion.

## Dependencies and Integration Points

It integrates `<functional>`, `<mutex>`, and libhdfs++ status types with `FileSystem::Find` and `FileSystem::SetReplication` callbacks.

## Risks and Edge Cases

Counter underflow, missing locking, or invoking the final handler more than once would break command completion. Large directory trees can create many outstanding requests.

## Test Signals

Tests should cover empty trees, directory-only trees, mixed file/directory trees, first-error preservation, and asynchronous callback reordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/internal/set-replication-state.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc` implements shared native helper routines for connecting to HDFS, streaming file contents, and parsing URIs. The source was read as a complete 140-line file for this report.

## Important APIs, Types, and Functions

`doConnect` loads default Hadoop resources, validates `core-site.xml` and `hdfs-site.xml`, builds `hdfs::Options`, optionally maximizes RPC timeout, creates an `IoService` and `FileSystem`, and connects to either the URI host/port or defaultFS. `readFile` opens an HDFS file, repeatedly `PositionRead`s into a static 1 MiB buffer, writes to a `FILE*`, and optionally deletes the source after EOF. `parse_path_or_exit` wraps `URI::parse_from_string` and exits on parse errors.

## Control Flow

Commands parse a path, call `doConnect`, then either invoke FileSystem metadata/mutation APIs or call `readFile` for data transfer. EOF is detected by `Status::is_invalid_offset()` in `readFile`.

## State and Persistence Behavior

The helper owns transient `ConfigParser`, `Options`, `IoService`, `FileSystem`, and `FileHandle` objects. `readFile` can persist bytes to a local file handle and can delete the HDFS source when `to_delete` is true.

## Dependencies and Integration Points

It integrates libhdfs++ configuration loading, URI handling, HDFS file IO, stderr diagnostics, and process termination for all native tools.

## Risks and Edge Cases

The static read buffer is not thread-safe, many failures call `exit(EXIT_FAILURE)` instead of returning errors, `IoService` lifetime is hidden behind `FileSystem`, and treating invalid offset as EOF depends on libhdfs++ behavior.

## Test Signals

MiniDFSCluster connection tests, defaultFS and explicit host/port tests, malformed configuration tests, partial read failure tests, stdout/local file transfer tests, and move-to-local delete-after-copy checks validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.cc -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h` declares shared libhdfs++ helper functions used by the native command-line tools. The source was read as a complete 37-line file for this report.

## Important APIs, Types, and Functions

The namespace `hdfs` exposes `doConnect(hdfs::URI&, bool)`, `readFile(std::shared_ptr<FileSystem>, std::string, off_t, std::FILE*, bool)`, and `parse_path_or_exit(const std::string&)`.

## Control Flow

The header has no executable flow, but defines the common path for URI parsing, FileSystem construction/connection, and HDFS-to-local/stdout streaming used by commands such as `tail`, `get`, and `moveToLocal`.

## State and Persistence Behavior

No state is declared here. Implementations may open HDFS files, write local file handles, or delete HDFS paths based on arguments.

## Dependencies and Integration Points

It includes `hdfspp/hdfspp.h` and `<mutex>`, making libhdfs++ types available to command implementations.

## Risks and Edge Cases

The helper API exits the process on several failures rather than returning status, which makes callers simpler but harder to unit-test and compose.

## Test Signals

Connection tests with explicit URI and defaultFS, malformed URI tests, and file-read smoke tests through commands that call these helpers are relevant.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/tools_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/dev-support/findbugsExcludeFile.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/dev-support/findbugsExcludeFile.xml

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/dev-support/findbugsExcludeFile.xml` is the module-local FindBugs/SpotBugs exclusion file for `hadoop-hdfs-nfs`. The source was read as a complete 18-line XML file for this report.

## Important APIs, Types, and Functions

The document contains a `FindBugsFilter` root element with no `Match` entries. It currently excludes nothing locally.

## Control Flow

There is no runtime flow. Static-analysis tooling reads the XML when configured and applies any listed suppressions.

## State and Persistence Behavior

The file persists analysis configuration only. It does not influence runtime gateway behavior.

## Dependencies and Integration Points

It is part of module developer support. The active POM references the global exclude file, so this local file is currently a placeholder unless external tooling includes it.

## Risks and Edge Cases

Adding broad suppressions here could hide real defects. Leaving it empty means module findings rely on global filters and code fixes.

## Test Signals

Run the module SpotBugs/FindBugs profile and confirm no unexpected local suppressions are needed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/dev-support/findbugsExcludeFile.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml` is the Maven module descriptor for Apache Hadoop `hadoop-hdfs-nfs`. The source was read as a complete 258-line file for this report.

## Important APIs, Types, and Functions

The POM declares parent `hadoop-project` version `3.6.0-SNAPSHOT`, artifact `hadoop-hdfs-nfs`, JAR packaging, compile/provided/test dependencies, a `dist` profile using `maven-assembly-plugin`, and SpotBugs configuration pointing at the global exclude file.

## Control Flow

During Maven builds the dependency graph supplies Hadoop common/HDFS/NFS, Netty, Jetty/Jersey, commons libraries, protobuf, servlet APIs, metrics, logging, and test frameworks. The `dist` profile packages the module with the Hadoop HDFS NFS assembly descriptor.

## State and Persistence Behavior

Build outputs are persisted under Maven target directories and optional distribution artifacts. The POM does not affect runtime state except through dependency versions/scopes and packaged resources.

## Dependencies and Integration Points

This module integrates `hadoop-nfs`, `hadoop-hdfs`, `hadoop-hdfs-client`, shaded Guava, Netty, Jetty, Jersey, commons-daemon, metrics, protobuf, JUnit 5, Mockito, AssertJ, and Hadoop test jars.

## Risks and Edge Cases

Dependency scope mistakes can produce missing runtime classes or oversized artifacts. The SpotBugs configuration uses only the global exclude file, so module-specific findings must be addressed or globally justified.

## Test Signals

`mvn -pl hadoop-hdfs-project/hadoop-hdfs-nfs test`, dependency analysis, SpotBugs, and `-Pdist package` validate this descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java` centralizes configuration key names and defaults for the HDFS NFS gateway. The source was read as a complete 95-line file for this report.

## Important APIs, Types, and Functions

`NfsConfigKeys` is a constants-only class. It defines server and mountd ports, transfer limits (`nfs.rtmax`, `nfs.wtmax`, `nfs.dtmax`), open-file cache size, stream timeout, export points, Kerberos keytab/principal, registration and port-monitoring settings, AIX compatibility, large upload behavior, HTTP/HTTPS addresses, metrics percentile intervals, NFS superuser, and UDP portmap timeout.

## Control Flow

There is no runtime flow beyond class loading. Other gateway components read these constants when constructing RPC programs, HTTP servers, caches, metrics, and security login state.

## State and Persistence Behavior

The file owns no mutable state. Values are defaults and lookup keys; actual configuration state lives in Hadoop `Configuration` instances and XML resources.

## Dependencies and Integration Points

It is consumed by `NfsConfiguration`, `Mountd`, `RpcProgramMountd`, `Nfs3`, `DFSClientCache`, `Nfs3HttpServer`, and metrics setup.

## Risks and Edge Cases

Changing defaults can alter exposed ports, security posture, transfer sizing, cache behavior, or HTTP binding. The default `nfs.port.monitoring.disabled=true` allows insecure ports unless deployment overrides it.

## Test Signals

Configuration-deprecation tests, gateway startup tests with overridden ports and export points, HTTP address tests, and export/superuser access tests exercise these constants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfigKeys.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java` extends `HdfsConfiguration` for the NFS gateway and registers deprecated configuration key mappings. The source was read as a complete 73-line file for this report.

## Important APIs, Types, and Functions

`NfsConfiguration` has a static initializer that calls `addDeprecatedKeys()`. The helper registers `Configuration.DeprecationDelta` mappings from older `nfs3.*`, `dfs.nfs3.*`, and related keys to current `NfsConfigKeys`, `Nfs3Constant`, and `IdMappingConstant` names.

## Control Flow

When the class is loaded, Hadoop's global configuration deprecation table is updated. Gateway startup then uses this subclass so old XML properties remain readable under new keys.

## State and Persistence Behavior

No instance state is added beyond `HdfsConfiguration`. The persistent effect is process-global deprecation metadata inside Hadoop configuration handling.

## Dependencies and Integration Points

It integrates HDFS configuration defaults, NFS constants, and user/group ID mapping constants. `Mountd` and `Nfs3` create this configuration at startup.

## Risks and Edge Cases

Missing a deprecation mapping silently breaks compatibility for existing deployments. Since mappings are process-global, test isolation must account for static registration.

## Test Signals

Configuration tests should set deprecated keys and assert current keys resolve to the same values; gateway startup with legacy XML names is the best integration signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/conf/NfsConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java` is the mount daemon entry point for the HDFS NFS gateway. The source was read as a complete 45-line file for this report.

## Important APIs, Types, and Functions

`Mountd` extends `MountdBase`. Its constructor builds a `RpcProgramMountd` with `NfsConfiguration`, optional registration socket, and insecure-port policy. `main` creates a default `NfsConfiguration`, constructs `Mountd`, and starts it with registration enabled.

## Control Flow

Standalone startup is simple: create config, create RPC program through the constructor, and call `start(true)`. In normal NFS gateway startup, `Nfs3` owns a `Mountd` instance and starts it before the NFSv3 RPC server.

## State and Persistence Behavior

The daemon owns process-lifetime RPC server state through `MountdBase`. Mount entries and export mappings live inside `RpcProgramMountd`, not in this wrapper.

## Dependencies and Integration Points

It integrates the Hadoop NFS mount base class, `RpcProgramMountd`, UDP registration socket handling, and `NfsConfiguration` defaults.

## Risks and Edge Cases

Standalone `main` passes `allowInsecurePorts=true`, which differs from configurable `Nfs3.startService` policy. Constructor failures propagate as `IOException`.

## Test Signals

`TestMountd`, export table tests, and `Nfs3` startup tests verify daemon construction and mountd/NFS lifecycle ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/Mountd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java` implements the ONC/RPC mount protocol program used by the HDFS NFS gateway. The source was read as a complete 283-line file for this report.

## Important APIs, Types, and Functions

`RpcProgramMountd` extends `RpcProgram` and implements `MountInterface`. Key APIs are constructor, `addExports`, `nullOp`, `mnt`, `dump`, `umnt`, `umntall`, `handleInternal`, `isIdempotent`, and testing accessor `getExports`. It defines mountd program/version constants and stores synchronized `mounts`, export path-to-URI map, `NfsConfiguration`, and `NfsExports` host matcher.

## Control Flow

Construction registers the RPC program, resolves configured export paths through `Nfs3Utils.getResolvedURI`, initializes host access matching, configures UGI, and logs in from keytab when configured. `handleInternal` decodes the RPC procedure and dispatches to mount operations. `MNT` enforces host exports and port monitoring, resolves a DFS file handle from the export directory file ID and namenode ID, records the mount entry, and writes an XDR response.

## State and Persistence Behavior

Export mappings are built at startup and kept in memory. Current mounts are an in-memory synchronized list used by `DUMP`, `UMNT`, and `UMNTALL`; they are not durable. HDFS file IDs and namenode IDs are encoded into returned file handles.

## Dependencies and Integration Points

It integrates Netty, ONC/RPC XDR, Hadoop NFS mount response types, HDFS `DFSClient`, `NfsExports`, Kerberos login, and `Nfs3Utils` URI/namenode helpers.

## Risks and Edge Cases

Access-control errors must not leak handles. Export path matching is exact, hostnames are recorded from reverse DNS, `HashMap` export iteration order is not stable, and each mount opens a short-lived `DFSClient` without explicit close in this method.

## Test Signals

`TestExportsTable`, `TestViewfsWithNfs3`, mount access tests, port-monitoring tests, and RPC procedure dispatch tests cover this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/mount/RpcProgramMountd.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java` provides the asynchronous data-operation executor used by the NFSv3 gateway, currently for write-back tasks. The source was read as a complete 141-line file for this report.

## Important APIs, Types, and Functions

`AsyncDataService` owns a `ThreadPoolExecutor` with one core thread, four max threads, 60-second keepalive, a `LinkedBlockingQueue`, and `SubjectInheritingThread` factory. Package-private methods include `execute`, `shutdown`, and `writeAsync`. Nested `WriteBackTask` wraps an `OpenFileCtx` and calls `executeWriteBack()`.

## Control Flow

`writeAsync` creates a `WriteBackTask` and schedules it through synchronized `execute`. Worker threads run `OpenFileCtx.executeWriteBack()` and log any thrown `Throwable` so the executor thread survives.

## State and Persistence Behavior

Executor and thread group state are process-local. Durable effects are HDFS writes performed by `OpenFileCtx`, not by the executor itself.

## Dependencies and Integration Points

It integrates Java concurrency utilities, Hadoop `SubjectInheritingThread` for security context propagation, and NFS write-management classes.

## Risks and Edge Cases

The unbounded queue can accumulate work, `shutdown` does not await termination despite the comment, and callers must ensure only one write-back task per file is queued or executing.

## Test Signals

Write-path tests in `TestWrites`, out-of-order write tests, executor shutdown tests, and failure-injection tests around `OpenFileCtx.executeWriteBack()` validate this component.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/AsyncDataService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java` caches `DFSClient` and `FSDataInputStream` instances for NFS gateway users and namenodes. The source was read as a complete 357-line file for this report.

## Important APIs, Types, and Functions

Important types are private cache keys `DfsClientKey` and `DFSInputStreamCacheKey`, constructor, `prepareAddressMap`, `closeAll`, `clientLoader`, `getUserGroupInformation`, removal listeners, `inputStreamLoader`, `getDfsClient`, `getDfsInputStream`, and `invalidateDfsInputStream`. It uses Guava `LoadingCache` with max sizes 256 clients and 1024 input streams, and input streams expire after 10 minutes of access inactivity.

## Control Flow

Startup resolves configured export paths to HDFS URIs and builds `namenodeUriMap`, rejecting real namenode-ID collisions. Cache misses create proxy UGI for the effective user, relogin the real user from keytab if needed, and construct a `DFSClient` to the mapped namenode. Input-stream cache misses open a DFS input stream and wrap it. Removal listeners close clients and streams.

## State and Persistence Behavior

The caches are long-lived process memory. Shutdown hook `CacheFinalizer` closes cached clients. HDFS state is not persisted here, but cached clients and streams hold remote resources until eviction, invalidation, or shutdown.

## Dependencies and Integration Points

It integrates HDFS `DFSClient`, Hadoop `FileSystem`, UGI proxy users, `ShutdownHookManager`, `MultipleIOException`, shaded Guava caches, and `Nfs3Utils` namenode/export resolution.

## Risks and Edge Cases

`getDfsClient` and `getDfsInputStream` return null after loader failures, so callers must guard. Cache sizing and TTL affect resource pressure. Namenode ID hash collisions are explicitly detected only when authorities differ.

## Test Signals

`TestDFSClientCache`, `TestViewfsWithNfs3`, export collision tests, cache eviction/close tests, and Kerberos/proxy-user tests are the relevant signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/DFSClientCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java` starts and stops the HDFS NFSv3 gateway and its companion mount daemon. The source was read as a complete 81-line file for this report.

## Important APIs, Types, and Functions

`Nfs3` extends `Nfs3Base`, stores `Mountd mountd`, exposes constructors, `getMountd`, `startServiceInternal`, static `startService`, `stop`, and `main`.

## Control Flow

Construction creates the NFSv3 RPC program through `RpcProgramNfs3.createRpcProgramNfs3` and constructs `Mountd` with the same registration socket and port policy. `startService` logs startup, reads insecure-port policy from configuration, starts mountd, then starts the NFS server. `stop` stops the NFS server first, then mountd.

## State and Persistence Behavior

Runtime state is the pair of RPC servers and their sockets, registrations, metrics, caches, and write managers. No durable state is owned here; HDFS mutations occur in the RPC program.

## Dependencies and Integration Points

It integrates `Nfs3Base`, `RpcProgramNfs3`, `Mountd`, `NfsConfiguration`, startup logging, and `NfsConfigKeys.DFS_NFS_PORT_MONITORING_DISABLED_KEY`.

## Risks and Edge Cases

Lifecycle ordering matters: clients need mountd available for handles before NFS operations. Shared registration socket handling and insecure-port policy must remain consistent between mountd and NFS.

## Test Signals

Gateway startup/shutdown tests, `TestExportsTable`, `TestNfs3HttpServer`, and tests that inspect `getMountd()` validate this wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java` encapsulates the HTTP/HTTPS info server for the NFSv3 gateway. The source was read as a complete 110-line file for this report.

## Important APIs, Types, and Functions

`Nfs3HttpServer` stores `infoPort`, `infoSecurePort`, `HttpServer2 httpServer`, and `NfsConfiguration conf`. Key methods are constructor, `start`, `stop`, `getPort`, `getSecurePort`, `getServerURI`, and `getHttpAddress`.

## Control Flow

`start` resolves HTTP and HTTPS socket addresses from config, uses `DFSUtil.getHttpServerTemplate` with NFS Kerberos key/principal settings, builds and starts `HttpServer2`, then records connector ports according to `DFSUtil.getHttpPolicy`. `stop` wraps server stop exceptions in `IOException`.

## State and Persistence Behavior

Server/socket state is process-local. No durable state is written by this class; exposed metrics/status are served from other runtime components.

## Dependencies and Integration Points

It integrates Hadoop HTTP policy, `HttpServer2`, `DFSUtil`, `NetUtils`, and NFS HTTP/HTTPS configuration keys.

## Risks and Edge Cases

Connector index ordering depends on HTTP policy. Binding to wildcard addresses and deriving client URI scheme need tests for HTTP_ONLY, HTTPS_ONLY, and mixed policies.

## Test Signals

`TestNfs3HttpServer` covers configured ports, secure policy behavior, and server URI exposure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3HttpServer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java` defines mutable metrics for NFSv3 gateway RPC activity, bytes, and selected latency quantiles. The source was read as a complete 219-line file for this report.

## Important APIs, Types, and Functions

`Nfs3Metrics` is annotated with Metrics2 annotations. It owns `MutableRate` fields for NFSv3 procedures, `MutableCounterLong` fields for bytes, quantile arrays for read/write/commit latencies, a `MetricsRegistry`, gateway name, and `JvmMetrics`. `create` registers the source with `DefaultMetricsSystem`; `add*` methods update rates and quantiles.

## Control Flow

Construction tags the registry with session ID and creates quantiles for configured percentile intervals. RPC handlers call `addGetattr`, `addRead`, `addWrite`, `addCommit`, and related methods with nanosecond latencies; read/write/commit additionally feed quantile trackers.

## State and Persistence Behavior

Metrics are in-memory counters/rates/quantiles exported through Hadoop Metrics2. They reset on process restart and do not persist to HDFS.

## Dependencies and Integration Points

It integrates Metrics2 annotations, `DefaultMetricsSystem`, `JvmMetrics`, DFS metrics session ID, and `NfsConfigKeys.NFS_METRICS_PERCENTILES_INTERVALS_KEY`.

## Risks and Edge Cases

Empty percentile intervals produce empty quantile arrays, which is valid. Incorrect latency units would skew dashboards because comments and APIs assume nanoseconds.

## Test Signals

Metrics registration tests, RPC handler tests that assert counters/rates move, and configured percentile interval tests validate this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Metrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java` provides NFSv3 gateway utility methods for inode paths, attribute conversion, weak-cache consistency data, socket writes, access-right calculation, byte conversions, elapsed time, namenode IDs, and export URI resolution. The source was read as a complete 273-line file for this report.

## Important APIs, Types, and Functions

Important APIs include `getFileIdPath`, `getFileStatus`, `getNfs3FileAttrFromFileStatus`, `getFileAttr`, `getDirSize`, `getWccAttr`, `createWccData`, `writeChannel`, `writeChannelCommit`, `getAccessRights`, `getAccessRightsForUserGroup`, `bytesToLong`, `longToByte`, `getElapsedTime`, `getNamenodeId`, and `getResolvedURI`.

## Control Flow

Most helpers are straight conversions. Attribute conversion maps HDFS status into NFS file type, nlink, mode, uid/gid, size, file ID, and times. Access checks choose owner, group/auxiliary group, or other permission bits. `getResolvedURI` resolves viewfs mount points or HDFS export paths and rejects non-HDFS backing filesystems.

## State and Persistence Behavior

The class is stateless. It reads HDFS metadata through `DFSClient` and writes network responses to Netty channels but does not persist durable data itself.

## Dependencies and Integration Points

It integrates HDFS protocol status, Hadoop NFS attribute/response types, Netty channels, ONC/RPC XDR, ID mapping, viewfs, and DFS namenode address resolution.

## Risks and Edge Cases

Directory size is synthetic, file IDs are 64-bit despite old client concerns, access-right mapping must match NFSv3 semantics, byte conversion assumes exactly eight bytes, and viewfs export resolution chooses the first matching mount prefix.

## Test Signals

`TestNfs3Utils`, `TestViewfsWithNfs3`, `TestRpcProgramNfs3`, readdir/read/write tests, and namenode-ID/export resolution tests cover this utility surface.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/Nfs3Utils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java

## Purpose

`sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java` models half-open byte offset ranges for NFS read/write coordination. The source was read as a complete 77-line file for this report.

## Important APIs, Types, and Functions

`OffsetRange` stores immutable `min` and `max`, validates `min >= 0`, `max >= 0`, and `min < max`, exposes package-private getters, overrides `hashCode`, `equals`, and `toString`, and provides `ReverseComparatorOnMin` ordering by descending min then descending max.

## Control Flow

Construction validates arguments with `Preconditions.checkArgument`. Comparisons and equality are deterministic value operations. Write-management classes use the comparator for pending-write range ordering.

## State and Persistence Behavior

Instances are immutable in-memory keys/ranges. Persistence of write data is handled elsewhere by `OpenFileCtx` and HDFS streams.

## Dependencies and Integration Points

It depends on Hadoop `Preconditions` and is used in write-path tests and pending write maps in the NFS gateway.

## Risks and Edge Cases

Single-point ranges such as `[5,5]` are rejected. The hash code is a simple cast of `min ^ max`, which is adequate for small maps but can collide. Package-private constructor/getters constrain use to the package.

## Test Signals

`TestOffsetRange`, `TestWrites`, and `TestOpenFileCtxCache` validate constructor guards, comparator ordering, equality, and use as pending-write keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-nfs/src/main/java/org/apache/hadoop/hdfs/nfs/nfs3/OffsetRange.java -->
