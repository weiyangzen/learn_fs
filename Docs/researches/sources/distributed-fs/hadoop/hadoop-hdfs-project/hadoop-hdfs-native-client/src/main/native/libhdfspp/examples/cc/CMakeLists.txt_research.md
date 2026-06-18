# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/CMakeLists.txt

## Purpose
This CMake file groups C++ libhdfs++ examples.

## Important APIs, Control Flow, and State
It adds `../../tools` as an include directory, then adds subdirectories `cat`, `gendirs`, `find`, and `connect_cancel`. It has no runtime state.

## Dependencies and Integration Points
The examples share `tools_common` helpers for URI parsing and filesystem connection. The parent examples directory includes this file only in non-library-only builds.

## Risks and Test Signals
The relative include path couples examples to the local tools layout. Build tests should verify all child targets configure after tools_common is defined and that disabling examples avoids these dependencies.
