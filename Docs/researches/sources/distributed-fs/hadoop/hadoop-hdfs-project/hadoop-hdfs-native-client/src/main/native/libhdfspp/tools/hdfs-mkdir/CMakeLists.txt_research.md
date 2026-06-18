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
