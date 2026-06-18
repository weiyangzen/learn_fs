# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs/CMakeLists.txt

## Purpose
This CMake file defines the native libhdfs build target, object reuse, link dependencies, output configuration, and several native test executables for Hadoop's HDFS native client.

## Important build targets
`HDFS_SOURCES` includes `exception.c`, `jni_helper.c`, `hdfs.c`, `jclasses.c`, and OS-specific mutex and thread-local storage implementations. `hdfs_obj` is an object library built as position-independent code. `hadoop_add_dual_library(hdfs ...)` creates the dual static/shared libhdfs target from `hdfs_obj`, x-platform objects, and x-platform C API objects. Test targets include `test_libhdfs_ops`, `test_libhdfs_threaded`, `test_libhdfs_zerocopy` on non-Windows/non-Apple, and `test_libhdfs_vecsum` on non-Windows.

## Control flow and integration
The file sets `LIBHDFS_DLL_EXPORT`, configures include directories for generated JNI headers, native sources, OS abstractions, and libhdfspp, then builds reusable objects before linking the public hdfs library with JVM, optional `dl`, and OS libraries. Test helper macros build, link, and register tests against `hdfs_static`, `native_mini_dfs`, OS thread code, and platform-specific libraries.

## State and persistence
Build state is CMake target state. It sets libhdfs `SOVERSION` to `0.0.0` and uses `hadoop_dual_output_directory` to place outputs under `${OUT_DIR}`.

## Dependencies
It depends on Hadoop's native CMake helper macros, `${JNI_INCLUDE_DIRS}`, `${JAVA_JVM_LIBRARY}`, `${OS_DIR}`, `${OS_LINK_LIBRARIES}`, `x_platform` object targets, and platform tests for `NEED_LINK_DL`, `WIN32`, `APPLE`, and `CMAKE_SYSTEM_NAME`.

## Risks
Tests are platform-gated, so zero-copy and vecsum coverage can disappear on Windows/macOS. `hdfs_obj` exists to reuse objects without public link dependencies; changes to target linking can accidentally pull JVM linkage into helper binaries or omit required platform objects. The include path reaches into `../libhdfspp/lib`, making libhdfs tests sensitive to adjacent native-client layout.

## Test signals
Successful configuration should produce libhdfs and register the native tests. Link failures usually reveal missing JNI, JVM, dl, thread, rt, or OS abstraction dependencies. Platform-specific skips are intentional.
