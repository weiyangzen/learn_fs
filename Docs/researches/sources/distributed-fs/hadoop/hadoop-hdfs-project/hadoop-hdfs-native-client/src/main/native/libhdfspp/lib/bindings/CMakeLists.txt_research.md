# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/bindings/CMakeLists.txt

## Purpose
This CMake file groups libhdfs++ language bindings.

## Important APIs, Control Flow, and State
It adds the `c` subdirectory. There is no runtime behavior or persistent state.

## Dependencies and Integration Points
The parent `lib/CMakeLists.txt` includes this directory. The C binding target contributes object files to the main libhdfs++ libraries and provides the C ABI used by `hdfs_ext.h` examples.

## Risks and Test Signals
This is low-risk build plumbing. Tests should verify the C binding target is included in top-level object aggregation and that disabling or moving binding directories fails loudly.
