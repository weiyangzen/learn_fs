# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-examples/CMakeLists.txt

## Purpose
Builds small libhdfs example binaries.

## Important APIs, Types, And Functions
Includes libhdfs/JNI/generated headers and creates executables `hdfs_read` from `libhdfs_read.c` and `hdfs_write` from `libhdfs_write.c`, both linked with `hdfs`.

## Control Flow
CMake configures include directories, adds two executables, and links them.

## State, Persistence, And Dependencies
Build outputs are example binaries. Dependencies include libhdfs target, JNI headers, generated javah headers, OS-specific native directory, and generated config.

## Integration Points
Entered from top-level native CMake; examples demonstrate the public C API and can be manually run against a configured HDFS cluster.

## Risks
No tests are registered here, so examples may compile but not be exercised. Runtime still depends on classpath and libjvm/libhdfs paths.

## Test Signals
Successful build and manual read/write execution validate the examples.
