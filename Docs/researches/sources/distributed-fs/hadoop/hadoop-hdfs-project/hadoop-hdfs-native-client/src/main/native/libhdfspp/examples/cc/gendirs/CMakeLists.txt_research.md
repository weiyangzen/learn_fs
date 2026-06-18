# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/gendirs/CMakeLists.txt

## Purpose
This CMake file builds the C++ `gendirs` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates executable `gendirs` from `gendirs.cc`, and links `tools_common` plus `hdfspp_static`.

## Dependencies and Integration Points
The target demonstrates asynchronous `FileSystem::Mkdirs` and common tools connection helpers. It is included from the C++ examples group.

## Risks and Test Signals
The example can generate a large number of async calls depending on input fanout/depth, so integration tests should use bounded trees. Build tests should verify target creation and linkage.
