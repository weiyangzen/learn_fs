# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/CMakeLists.txt

## Purpose
CMake setup for native libhdfs test support library and one native MiniDFS test target.

## Important APIs, Types, And Functions
Includes libhdfs/JNI/libhdfspp headers, builds `native_mini_dfs` from native cluster wrapper and JNI helper sources, builds `test_native_mini_dfs`, links with JVM, and registers `test_test_native_mini_dfs`.

## Control Flow
CMake declares include directories, creates a static/shared support library target from C sources and platform objects, creates executable test target, links it, and adds it to CTest.

## State, Persistence, And Dependencies
Build outputs include support library and test executable. Depends on Java JVM library, JNI headers, libhdfs internal sources, platform mutex/TLS sources, and x-platform objects.

## Integration Points
The `native_mini_dfs` library is linked by FUSE tests and other native libhdfs tests.

## Risks
This file only registers `test_native_mini_dfs`; other libhdfs tests may be defined elsewhere via top-level helper functions. It compiles internal libhdfs implementation files directly, so source layout changes affect tests.

## Test Signals
CTest target `test_test_native_mini_dfs` validates native MiniDFS wrapper construction/linking.
