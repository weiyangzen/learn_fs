# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/fgl/TestFSNLockBenchmarkThroughput.java

## Purpose

`TestFSNLockBenchmarkThroughput` runs the throughput benchmark against both fine-grained and global FSNamesystem lock providers with several read/write ratios, test counts, and client counts.

## Important APIs, Types, and Functions

The class is tagged `slow`. It uses `MiniQJMHACluster`, `MiniDFSCluster`, `DFS_NAMENODE_LOCK_MODEL_PROVIDER_KEY`, `DFS_HA_TAILEDITS_INPROGRESS_KEY`, `DFS_QJOURNAL_SELECT_INPUT_STREAMS_TIMEOUT_KEY`, `FineGrainedFSNamesystemLock`, `GlobalFSNamesystemLock`, `FSNLockManager`, `ToolRunner`, and `FSNLockBenchmarkThroughput`.

## Control Flow

Each public test delegates to `testBenchmarkThroughput` with a lock model flag and workload parameters. The helper builds a QJM HA cluster with ten DataNodes, transitions NN0 active, obtains a `FileSystem`, constructs benchmark arguments, runs the tool, asserts return code `0`, and shuts down the QJM cluster.

## State and Persistence Behavior

The tests create real HDFS namespace workload under `/tmp/fsnlock/benchmark/throughput` and rely on cluster shutdown for cleanup. HA edit tailing and journal state are active because the benchmark runs in a QJM topology.

## Dependencies and Integration Points

It integrates the benchmark tool, lock model provider selection, QJM shared edits, HA active transition, DFS client operations, and MiniDFSCluster DataNode capacity.

## Risks and Edge Cases

The workloads are large and concurrency-heavy, especially `1000` clients, making the class slow and resource-sensitive. The tests assert success only, not relative throughput.

## Test Signals

Signals are six successful runs: three fine-grained-lock configurations and three global-lock configurations, each returning `0` from `ToolRunner.run`.
