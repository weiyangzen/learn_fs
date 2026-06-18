# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/test/java/org/apache/hadoop/hdfs/server/federation/metrics/TestRouterClientMetrics.java

## Purpose
This test verifies router client activity metrics for individual client protocol operations and their concurrent fan-out variants.

## Important APIs, Types, and Functions
It uses `MiniRouterDFSCluster`, `RouterConfigBuilder().metrics().rpc().quota()`, `MockResolver`, router `FileSystem`, router RPC server methods, and metrics assertions on the `RouterClientActivity` metrics source. Operations include listing, create, get server defaults, set/get quota, renew lease, datanode report, and slow datanode report.

## Control Flow
The class-level setup starts a two-subcluster mini-router cluster with datanodes, routers, and registered NameNodes. Per-test setup installs mock locations, deletes files, creates NameNode test directories, gets the first router filesystem, and adds an additional root mount to the second nameservice so root operations fan out. Each test invokes one router operation and asserts the expected operation counter; fan-out operations assert both the per-NameNode count of two and the concurrent counter of one.

## State and Persistence
Filesystem and resolver state are reset per test. Metrics counters are held in Hadoop's in-process metrics system. No external persistence is involved.

## Dependencies and Integration Points
The test integrates the client-facing filesystem API, direct `RouterRpcServer` calls, `MockResolver` multi-destination root routing, quota support, and Hadoop metrics test helpers.

## Risks and Test Signals
Absolute counter assertions assume the metrics source is clean enough after setup for each method. Fan-out counts depend on the extra root mount to both nameservices. Passing tests signal that router metrics names are wired for both simple and concurrent versions of each operation and that direct RPC-server calls record client activity.
