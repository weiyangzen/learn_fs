# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfs-tests/native_mini_dfs.h

## Purpose
`native_mini_dfs.h` defines the C test-facing interface for controlling a Java `MiniDFSCluster` from native libhdfs tests.

## Important APIs and types
The key type is `struct NativeMiniDfsConf`, with `doFormat`, `webhdfsEnabled`, `namenodeHttpPort`, `configureShortCircuit`, and `numDataNodes`. The cluster object is opaque as `struct NativeMiniDfsCluster`. The header declares lifecycle, wait, NameNode port, NameNode HTTP address, and domain socket path accessors.

## Control flow and integration
Tests initialize `NativeMiniDfsConf`, call `nmdCreate`, wait with `nmdWaitClusterUp`, read the RPC port with `nmdGetNameNodePort`, connect with `hdfsBuilder`, then call `nmdShutdown` and `nmdFree`. Zero-copy tests additionally enable `configureShortCircuit` and pass `hdfsGetDomainSocketPath` into the libhdfs builder configuration.

## State and persistence
The header describes the desired Java cluster state but owns no storage. The configuration fields are consumed at cluster construction time. The opaque cluster owns runtime state inside `native_mini_dfs.c`.

## Dependencies
It includes `jni.h` for `jboolean` and `jint`, forward-declares `struct hdfsBuilder`, and uses C++ linkage guards.

## Risks
The struct is a native test contract, so changing field order or meaning can silently alter test cluster setup. The comments mention non-HA assumptions for NameNode accessors; future HA MiniDFS support would need API changes or clearer selection semantics.

## Test signals
Every MiniDFS native integration test includes this header. Basic lifecycle coverage is in `test_native_mini_dfs.c`; operational, threaded, stress, and zero-copy tests exercise richer combinations of its configuration fields.
