# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/CMakeLists.txt

## Purpose
This CMake file groups the C API examples for libhdfs++.

## Important APIs, Control Flow, and State
It adds the `cat` and `connect_cancel` subdirectories. It carries no runtime state and exists to keep the example tree modular.

## Dependencies and Integration Points
It is reached from `examples/CMakeLists.txt` and delegates target creation to each example's CMake file. The child targets use the C extension API declared in `hdfspp/hdfs_ext.h`.

## Risks and Test Signals
Build tests should ensure both child C examples configure and link in full builds, and that `HDFSPP_LIBRARY_ONLY` excludes them through the parent rather than leaving dangling targets.
