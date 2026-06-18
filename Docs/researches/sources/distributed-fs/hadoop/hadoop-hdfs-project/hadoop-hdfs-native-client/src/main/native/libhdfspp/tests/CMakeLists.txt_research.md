# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/CMakeLists.txt

## Purpose

This CMake file defines the native libhdfspp unit and integration test targets, common mock support, protobuf test generation, valgrind-enabled test registration, and conditional Hadoop mini-cluster tests.

## Important APIs, types, and functions

It sets libhdfs/libhdfspp source directory variables, includes generated JNI/protobuf paths, builds `test_common_obj` and `test_common` from `mock_connection.cc`, generates test protobuf sources from `test.proto` and `test_rpc_service.proto`, and defines `add_memcheck_test()`. It adds unit tests for URI, JNI failure, remote block reader, SASL digest MD5, retry policy, RPC engine, bad datanode handling, node exclusion, configuration, HDFS builder/config bugs, logging, IO service, user locks, and errors.

## Control flow, state, and persistence

Build-time control flow adds x-platform, utils, and tool test subdirectories unconditionally, then adds integration tests only when `HADOOP_BUILD` is true. For integration tests, it builds shim/static libraries and uses libhdfs test helper macros to run mini DFS tests. No runtime state is stored by this file.

## Dependencies and integration points

The file ties tests to `common`, `rpc`, `reader`, `fs`, `bindings_c`, `proto`, protobuf/absl, OpenSSL, SASL, Boost, JNI, and Hadoop native mini DFS. It also removes `JAVA_JVM_LIBRARY` from one libhdfs static-link path so JNI symbols can be overridden in `libhdfs_getjni_test.cc`.

## Risks and test signals

Risks include link-order fragility, duplicated libraries, and tests that only build under `HADOOP_BUILD`. The valgrind wrapper is conditional on `MEMORYCHECK_COMMAND` and `SKIP_VALGRIND`. Good signals are all unit targets building, protobuf-generated tests compiling, no duplicate symbol failures in wrapper/shim tests, and mini DFS tests passing when Hadoop Java infrastructure is present.
