# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/tests/hdfspp_mini_dfs_smoke.cc

## Purpose

This smoke test verifies that a native mini DFS cluster can start and accept both C++ and C libhdfspp connections.

## Important APIs, types, and functions

It defines `HdfsMiniDfsSmokeTest` with a `MiniCluster` member and one `SmokeTest` test. The test calls `cluster.connect()` and `cluster.connect_c()` and asserts that both returned handles are non-null.

## Control flow, state, and persistence

The fixture constructs the mini DFS cluster before the test and destroys it afterward through `MiniCluster` RAII. The test performs two connection attempts, one through `FileSystem` and one through `hdfsBuilderConnect()`. Cluster state is temporary.

## Dependencies and integration points

It includes `hdfspp_mini_dfs.h`, gmock/gmock through that header, and protobuf cleanup in `main()`. It is built only when `HADOOP_BUILD` enables mini DFS integration tests.

## Risks and test signals

This is a broad environment readiness signal rather than a feature-specific test. Failures can indicate Hadoop Java/native mini DFS setup issues, NameNode startup problems, C API connection regressions, or C++ connection regressions. It is useful before running larger integration suites.
