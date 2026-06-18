# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/find/CMakeLists.txt

## Purpose
This CMake file builds the C++ `find` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates executable `find` from `find.cc`, and links `tools_common` plus `hdfspp_static`.

## Dependencies and Integration Points
The target uses `FileSystem::Find` in both synchronous and asynchronous modes and common tools helpers for URI parsing and connection setup.

## Risks and Test Signals
The target name `find` can collide with packaging conventions. Tests should compile and run both sync and async modes against known directory trees with wildcard paths and names.
