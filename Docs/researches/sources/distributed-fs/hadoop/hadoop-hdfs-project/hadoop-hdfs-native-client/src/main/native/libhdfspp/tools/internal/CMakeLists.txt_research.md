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
