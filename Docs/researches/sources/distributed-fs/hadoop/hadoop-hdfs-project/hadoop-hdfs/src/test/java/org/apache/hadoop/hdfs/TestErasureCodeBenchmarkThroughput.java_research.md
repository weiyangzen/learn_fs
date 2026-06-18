# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestErasureCodeBenchmarkThroughput.java

## Purpose
Tests the `ErasureCodeBenchmarkThroughput` tool against a live MiniDFSCluster for replicated and EC data paths. It validates that benchmark subcommands run successfully and that cleanup removes generated EC files.

## Important APIs and Types
Uses `ToolRunner.run`, `ErasureCodeBenchmarkThroughput`, `MiniDFSCluster`, `DistributedFileSystem.enableErasureCodingPolicy`, `FileSystem.listStatus`, `PathFilter`, and tool constants such as `EC_DIR`, `REP_DIR`, and `getFilePath`.

## Control Flow
`setup()` starts a cluster with enough DataNodes for the benchmark EC policy and enables that policy. `runBenchmark` asserts that each tool invocation returns `0`. `testReplicaReadWrite` runs `write`, `gen`, and `read` for replicated mode. `testECReadWrite` does the same for EC mode. `testCleanUp` generates EC files, runs `clean`, then filters the EC directory for the expected benchmark filename prefix and asserts zero matches.

## State, Persistence, Dependencies, Integration
State is test data written under the benchmark's replicated and EC directories. The tests depend on the benchmark tool's command parser, worker behavior, and path naming scheme. Integration is intentionally tool-level rather than direct DFS API calls.

## Risks and Test Signals
The key signal is command success across write/generate/read/clean flows. The cleanup assertion is the only content-level verification; throughput values are not validated, so regressions in performance reporting could pass if command exits remain successful.
