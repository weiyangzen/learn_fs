# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfspp_mini_dfs.h

## Purpose

This header provides RAII helpers for tests that need a native mini DFS cluster and both C++ and C libhdfspp connections.

## Important APIs, types, and functions

It defines `TEST_BLOCK_SIZE`, atomic counters for generated directories/files, `FSHandle`, `HdfsHandle`, and `MiniCluster`. `HdfsHandle` owns an `hdfsFS`, disconnects in its destructor, and has `newDir()` / `newFile()` helpers. `MiniCluster` wraps `nmdCreate()`, `nmdWaitClusterUp()`, `nmdShutdown()`, and connection helpers `connect()` and `connect_c()`.

## Control flow, state, and persistence

`MiniCluster` starts a one-node formatted short-circuit-enabled cluster in its constructor and shuts it down in its destructor. C++ connections create a `FileSystem` with an `IoService` and connect to localhost NameNode port. C connections use an `hdfsBuilder`, force a new instance, set NameNode host/port and block-size configs, and optionally set username. Test files and directories live in the mini cluster until it is destroyed.

## Dependencies and integration points

The header depends on libhdfs, libhdfspp C++ APIs, `native_mini_dfs.h`, `XPlatform::Syscall::ClearBufferSafely()`, protobuf/gmock headers, atomics, and strings. It supports `hdfs_ext_test.cc` and `hdfspp_mini_dfs_smoke.cc`.

## Risks and test signals

Risks include mini-cluster startup flakiness, mismatch between requested write size and hardcoded expected `1024` in `newFile()`, and resource leaks if assertions fire before RAII cleanup. Passing smoke and extension tests are strong signals that both C and C++ connection paths still work against real Hadoop services.
