# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/examples/cc/connect_cancel/CMakeLists.txt

## Purpose
This CMake file builds the C++ `connect_cancel` example.

## Important APIs, Control Flow, and State
It defines `LIBHDFSPP_DIR`, includes installed headers, links installed lib directories, creates `connect_cancel` from x-platform object files plus `connect_cancel.cc`, links `hdfspp_static`, and adds `../../lib` privately for internal headers.

## Dependencies and Integration Points
The target exercises `IoService`, `FileSystem::CancelPendingConnect`, configuration loading, and x-platform syscall helpers. It depends on object libraries created elsewhere in the build.

## Risks and Test Signals
The target is sensitive to object-library names and include ordering. Build tests should verify the target links in standalone and Hadoop-tree builds and that x-platform object dependencies are available.
