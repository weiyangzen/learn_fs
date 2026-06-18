# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/TestNamenodeCapacityReport.java

Purpose: Tests NameNode capacity, non-DFS usage, block pool usage percentages, same-disk storage tiering accounting, and xceiver load statistics for live, dead, decommissioning, and maintenance DataNodes.

Important APIs and functions: Uses `FSNamesystem` capacity getters, `DatanodeDescriptor` capacity fields, `DFSUtilClient` percent helpers, `FsDatasetTestUtils`, `DataNodeTestUtils.triggerHeartbeat`, and `DatanodeManager` admin operations. Helpers `checkClusterHealth`, `getNumDNInService`, `getInServiceXceiverAverage`, `startDecommissionOrMaintenance`, and `stopDecommissionOrMaintenance` centralize assertions.

Control flow: `testVolumeSize` configures reserved space, verifies DataNode and NameNode capacity arithmetic, creates open streams to account for reserved replica space, and triggers heartbeats. `testVolumeSizeWithSameDiskTiering` runs DISK and ARCHIVE volumes sharing a disk and verifies reserved/non-DFS space is not double counted. `testXceiverCountInternal` starts eight DataNodes, kills and restarts nodes, opens replicated write pipelines, transitions nodes into decommission or maintenance, closes streams, and checks total and in-service load after each stage.

State and persistence behavior: Namespace files and open write pipelines create block and xceiver state. Capacity state is reported through DataNode heartbeats into the NameNode. Admin states change DataNode service membership and affect in-service averages.

Dependencies and integration points: Integrates DataNode storage reports, FSNamesystem aggregate stats, block manager cluster stats, maintenance/decommission paths, HDFS client write pipeline behavior, and same-disk tiering configuration.

Risks: Capacity values depend on local filesystem capacity and MiniDFSCluster storage layout, so assertions use relationships rather than fixed totals. Xceiver load requires timely heartbeat propagation and short sleeps. Closing streams with decommissioned pipeline nodes can throw and is conditionally tolerated.

Test signals: Passing shows capacity excludes reserved space, percentages match helper math, same-disk tiering avoids double counting, and live/in-service node and xceiver load counts track node death and admin state transitions.
