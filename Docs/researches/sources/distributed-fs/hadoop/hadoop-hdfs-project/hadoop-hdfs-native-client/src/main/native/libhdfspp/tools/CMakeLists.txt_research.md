<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt

## Purpose
Top-level CMake build script for libhdfs++ command-line tools. It discovers Boost program_options, configures include/link roots, builds shared helper objects, and adds every individual HDFS command subdirectory.

## Important APIs, Types, And Functions
CMake declarations: `find_package(Boost 1.86 COMPONENTS program_options REQUIRED)`, `add_library(tools_common_obj OBJECT tools_common.cc)`, `add_library(tools_common $<TARGET_OBJECTS:tools_common_obj>)`, `add_subdirectory(internal)`, `add_library(hdfs_tool_obj OBJECT hdfs-tool.cc)`, `target_include_directories(hdfs_tool_obj PRIVATE ../tools)`, `add_subdirectory(hdfs-cat)`, `add_subdirectory(hdfs-chgrp)`, `add_subdirectory(hdfs-chown)`, `add_subdirectory(hdfs-chmod)`, `add_subdirectory(hdfs-find)`, `add_subdirectory(hdfs-mkdir)`, `add_subdirectory(hdfs-rm)`, `add_subdirectory(hdfs-ls)`, `add_subdirectory(hdfs-stat)`, `add_subdirectory(hdfs-count)`, `add_subdirectory(hdfs-df)`, `add_subdirectory(hdfs-du)`, `add_subdirectory(hdfs-get)`, `add_subdirectory(hdfs-copy-to-local)`, `add_subdirectory(hdfs-move-to-local)`, `add_subdirectory(hdfs-setrep)`, `add_subdirectory(hdfs-allow-snapshot)`, `add_subdirectory(hdfs-disallow-snapshot)`, `add_subdirectory(hdfs-create-snapshot)`, `add_subdirectory(hdfs-rename-snapshot)`, `add_subdirectory(hdfs-delete-snapshot)`, `add_subdirectory(hdfs-tail)`.

## Control Flow
CMake first resolves Boost and `LIBHDFSPP_DIR`, exposes include and link directories, creates `tools_common_obj/tools_common`, includes internal helper code, creates the shared `hdfs_tool_obj`, then processes each command subdirectory from `hdfs-cat` through `hdfs-tail`.

## State And Persistence
No runtime state. Build state is object libraries, command static libraries, and executable targets registered by child directories.

## Dependencies And Integration Points
Integrates the tool tree with installed libhdfs++ headers/libs, Boost program_options, common helpers, and all child command CMake files.

## Risks
Global `include_directories()` and `link_directories()` affect all child targets and can hide missing target-specific dependencies. Adding a new tool requires both a subdirectory and matching tests/install rules.

## Test Signals
Successful configuration and build of all command executable targets, plus parser test linkage against the same command libraries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tools/CMakeLists.txt -->
