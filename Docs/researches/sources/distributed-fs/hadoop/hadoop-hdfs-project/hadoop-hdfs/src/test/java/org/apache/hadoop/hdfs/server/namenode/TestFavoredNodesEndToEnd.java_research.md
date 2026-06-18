<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java -->
## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java

Purpose: `TestFavoredNodesEndToEnd` verifies that client-specified favored DataNodes influence block placement for create, append, and builder-based create APIs, and that HDFS gracefully falls back when favored nodes are absent or unsuitable.

Important APIs, types, and functions: it uses a 10-DataNode `MiniDFSCluster`, `DistributedFileSystem.create` overloads with `InetSocketAddress[]` favored nodes, `append(..., favoredNodes)`, `createFile(...).favoredNodes(...).build()`, `BlockPlacementPolicy`, `DatanodeInfo.setDecommissioned`, `getBlockLocations`, `DFSTestUtil.waitReplication`, and helper methods `getDatanodes`, `getStringForInetSocketAddrs`, `compareNodes`, and `getArbitraryLocalHostAddr`.

Control flow: class setup starts the cluster once and caches DataNodes. The main create test loops over ten files, picks three unique random DataNodes, creates a file with replication 3 and favored nodes, writes bytes, then asserts all block location names are among the favored nodes. The absent-node test passes three arbitrary localhost ports not belonging to the cluster and only asserts write/replication succeeds. The not-good-node test decommissions one favored node, creates a file with four candidate addresses, restores the node, and asserts replicas exclude the decommissioned address while remaining within the favored list. Append and builder tests mirror the create test through their respective APIs.

State and persistence behavior: state is live block placement and DataNode membership, not fsimage persistence. The decommission test temporarily mutates `DatanodeInfo` state and restores it with `stopDecommission`.

Dependencies and integration points: exercises NameNode block placement, client favored-node hint propagation, DataNode xfer addresses, block location reporting, replication wait logic, and create/append builder API integration.

Risks and edge cases: random selection uses current time, so it is non-deterministic but constrained to unique choices. Tests assume one block per file and exactly three hosts, which follows tiny writes and replication 3. The absent-node test has weak assertions beyond no failure and block-location shape. Address string comparison uses `ip:port` from `BlockLocation.getNames`, so formatting changes could break assertions.

Test signals: block locations must be a subset of selected favored nodes for create/append/builder paths, absent nodes must not fail writes, and a decommissioned favored node must be excluded from actual targets.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestFavoredNodesEndToEnd.java -->
