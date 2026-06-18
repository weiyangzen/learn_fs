# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/balancer/TestBalancerWithMultipleNameNodes.java

## Purpose
`TestBalancerWithMultipleNameNodes` verifies balancer behavior in federated HDFS clusters with multiple NameNodes and block pools. It tests datanode-level balancing and block-pool-specific balancing, including balancing only selected block pools while preserving usage in unselected pools.

## Important APIs, Types, and Functions
The file uses `MiniDFSNNTopology.simpleFederatedTopology`, `MiniDFSCluster`, `DFSTestUtil.setFederatedConfiguration`, `Balancer.run`, `BalancerParameters`, `BalancingPolicy.Pool`, `DatanodeStorageReport`, and `StorageReport`. The `Suite` helper bundles configuration, cluster, per-NameNode `ClientProtocol` instances, replication, and balancer parameters. Core helpers are `createFile`, `generateBlocks`, `wait`, `runBalancer`, `compareTotalPoolUsage`, `getStorageReports`, `unevenDistribution`, and `runTest`.

## Control Flow
`runTest` creates a federated cluster, writes files into each namespace, starts empty DataNodes, and runs the balancer over all or selected block pools. `unevenDistribution` first creates blocks in a formatted cluster, shuts it down, restarts without formatting with capacity scaled by number of NameNodes, injects custom block distributions into each block pool, builds `BalancerParameters` for selected pools, and runs the balancer. `runBalancer` captures pre-run storage reports for unselected pools, runs `Balancer.run`, polls all NameNode clients until datanode or pool utilization is within threshold, then compares total pool usage before and after for pools that should not have been touched.

## State and Persistence Behavior
State includes multiple block pools, per-NameNode file/block metadata, injected block reports, federated configuration, and datanode storage usage across pools. Clusters are explicitly shut down after each generated or test cluster. The tests depend on block pool IDs from namesystems to build selected pool sets.

## Dependencies and Integration Points
Integration points include federation configuration, NameNode RPC URI discovery, block-pool storage reports, balancer block-pool filtering, `BalancingPolicy.Pool`, and shared `TestBalancer` block distribution utilities.

## Risks and Test Signals
Risks include long waits without explicit timeout in `wait`, assumptions about client/name system ordering, block-pool ID selection by index, and high runtime for 600-second tests. Signals include balancer `SUCCESS`, all clients reporting consistent datanode used/capacity values, threshold-based balance checks, and unchanged total pool usage for unselected block pools.
