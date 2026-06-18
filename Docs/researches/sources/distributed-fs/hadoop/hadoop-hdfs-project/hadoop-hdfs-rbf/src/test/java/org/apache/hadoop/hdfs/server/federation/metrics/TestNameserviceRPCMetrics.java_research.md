# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestNameserviceRPCMetrics.java

## Purpose
This test verifies per-nameservice RPC metrics emitted by router proxy operations. It checks both single-namespace operations and concurrent fan-out operations.

## Important APIs, Types, and Functions
The test uses `MiniRouterDFSCluster`, `RouterConfigBuilder().metrics().rpc().quota()`, `MockResolver`, `FileSystem.listStatus()`, `RouterRpcServer.setBalancerBandwidth()`, and metrics assertions against `NameserviceRPCMetrics.NAMESERVICE_RPC_METRICS_PREFIX`.

## Control Flow
`globalSetUp()` starts a non-HA federated mini-cluster with two subclusters and three datanodes per nameservice, starts routers with metrics and RPC enabled, then registers NameNodes. Each test setup installs mock locations, clears files, creates test directories, obtains router filesystem/router references, and adds explicit `/target-ns0` and `/target-ns1` mounts. `testProxyOp()` lists each target path and verifies only that nameservice's `ProxyOp` counter increments. `testProxyOpCompleteConcurrent()` records ns0, ns1, and concurrent counters, calls `setBalancerBandwidth()`, and expects all three to increment by one.

## State and Persistence
Cluster filesystem state is reset before each test through mini-cluster helpers. Metrics are process-local Hadoop metrics counters. Resolver mount state is in the router's `MockResolver`.

## Dependencies and Integration Points
This class integrates router RPC metrics, the mock file resolver, mini DFS clusters, router-to-NameNode proxy calls, and Hadoop metrics test helpers. It validates metrics source naming by nameservice id and by the special `concurrent` source.

## Risks and Test Signals
Metrics counters can be cumulative across tests, so the concurrent test captures baselines while the single-op test asserts absolute values after setup reset. The unused `nnFS` field is benign. Passing tests signal correct attribution of proxy operations to the target nameservice and correct accounting for fan-out operations.
