# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/CMakeLists.txt

## Purpose
Top-level CMake build for the HDFS native client subtree.

## Important APIs, Types, And Functions
Configures project settings, compiler feature checks (`HAVE_BETTER_TLS`, `HAVE_INTEL_SSE_INTRINSICS`), generated `config.h`, OpenSSL detection, JNI setup, helper functions `build_libhdfs_test`, `add_libhdfs_test`, `link_libhdfs_test`, and subdirectories for libhdfs, tests, examples, libhdfs++, libwebhdfs, and FUSE.

## Control Flow
CMake sets MSVC or POSIX flags, configures JNI, checks `dlopen`, probes OpenSSL, adds core native subdirectories, conditionally builds libhdfs++ if `thread_local` works, conditionally adds libwebhdfs when required, and only adds FUSE on Linux when pkg-config finds `fuse`.

## State, Persistence, And Dependencies
Build state includes generated `config.h`, selected `OS_DIR`, output directory selection, detected OpenSSL and FUSE variables, and target objects reused by tests. It depends on `HadoopCommon`, `HadoopJNI`, C/C++ compilers, JNI headers, OpenSSL, pkg-config, and platform threading.

## Integration Points
This file is the native build entry invoked by Maven profiles. It wires libhdfs C API, native tests, examples, libhdfs++, optional libwebhdfs, and Linux FUSE client.

## Risks
Feature and library detection controls build coverage; missing optional dependencies silently skip components unless required. CMake standard toggles from C++17 to C++11 around thread_local checks can surprise subdirectories. Linux-only FUSE gating means FUSE code may be unbuilt on non-Linux CI.

## Test Signals
Configuration messages about OpenSSL, libhdfs++, libwebhdfs, and FUSE indicate coverage. `ctest` targets added by subdirectories are the runtime validation signal.
