# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfs_ext_test.cc

## Purpose

This integration-style test exercises extended libhdfspp C APIs against a mini DFS cluster.

## Important APIs, types, and functions

The `HdfsExtTest` fixture owns a `MiniCluster`. Tests cover block locations, used capacity, snapshot operations, mkdir/delete/rename, chmod/chown, EOF handling, exists, replication and times, default block size, hosts, read statistics, working directory, and connect/read event callbacks including throwing callbacks.

## Control flow, state, and persistence

Each test connects through `MiniCluster::connect_c()`, creates directories or files through `HdfsHandle` helpers, performs C API operations, and asserts returned metadata or errors. Snapshot tests create, rename, and delete snapshots around a test directory. Event tests install callbacks and verify invocation counts and exception handling. Mini DFS cluster state persists only for the fixture lifetime.

## Dependencies and integration points

The file depends on `hdfspp_mini_dfs.h`, libhdfspp C APIs, native mini DFS infrastructure, event callback plumbing, and gtest/gmock. It is compiled only under the CMake `HADOOP_BUILD` integration-test branch.

## Risks and test signals

This is one of the broadest end-to-end signals for C API compatibility. Risks are environmental: it needs Hadoop Java/native mini DFS support, can be slower or flaky, and relies on cluster semantics. It is valuable for catching regressions not visible in isolated unit tests, especially metadata, snapshot, and event behavior.
