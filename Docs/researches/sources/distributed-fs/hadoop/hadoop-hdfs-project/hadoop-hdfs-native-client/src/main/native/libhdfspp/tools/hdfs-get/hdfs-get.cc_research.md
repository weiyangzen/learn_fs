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
