# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/c/connect_cancel/CMakeLists.txt

## Purpose
This CMake file builds the C `connect_cancel_c` example demonstrating cancellation of pending libhdfs++ filesystem connection attempts.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, adds installed include/lib directories, creates `connect_cancel_c` from `connect_cancel.c` plus `$<TARGET_OBJECTS:x_platform_obj_c_api>`, links `hdfspp_static` and `uriparser2`, and adds `../../lib` as a private include directory.

## Dependencies and Integration Points
The target needs C bindings, x-platform syscall helpers for signal-safe output, and static libhdfs++. It is part of the C examples subtree.

## Risks and Test Signals
Object-library dependencies and private relative includes are sensitive to target names and build-tree layout. Build tests should verify the target links in full builds and that x-platform C API objects are available before this target is evaluated.
