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
