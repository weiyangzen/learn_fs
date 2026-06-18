# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/fuse-dfs/CMakeLists.txt

## Purpose
CMake sub-build for the Linux `fuse_dfs` executable and its native integration test.

## Important APIs, Types, And Functions
Defines `flatten_list`, applies `FUSE_CFLAGS`/`FUSE_LDFLAGS`, includes JNI/libhdfs/FUSE headers, builds `fuse_dfs` from all FUSE operation and support C files, and builds `test_fuse_dfs` from C test workload utilities.

## Control Flow
The parent only enters this directory when Linux FUSE is found. This file flattens pkg-config lists into strings, sets compiler/linker flags, creates the executables, and links `fuse_dfs` with FUSE, JVM, hdfs, math, pthread, and rt.

## State, Persistence, And Dependencies
Build outputs are executables in the native build tree. Dependencies include libfuse, libjvm, libhdfs, pthread, realtime library, and the `native_mini_dfs` test library.

## Integration Points
Connects the operation files registered by `fuse_dfs.c` with libhdfs and creates the executable invoked by wrapper scripts and FUSE tests.

## Risks
`CMAKE_SKIP_RPATH TRUE` makes runtime library paths environment-dependent. FUSE flags are appended globally. The test target is not explicitly added as a CTest here, so coverage depends on parent/test wiring.

## Test Signals
Successful link of `fuse_dfs` and `test_fuse_dfs`, plus runtime mount tests, validate this build file.
