# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyIsHot.java

Purpose: verifies that a standby NameNode is "hot" not only for namespace metadata but also for block-location information from block reports, replication changes, and DataNode restarts.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `NameNodeAdapter.getBlockLocations`, `LocatedBlocks`, `DatanodeInfo`, `BlockManagerTestUtil`, `DataNodeProperties`, and `GenericTestUtils.waitFor`.

Control flow: `testStandbyIsHot` starts two NNs and three DNs, writes a file, rolls the active edit log, waits for the standby to report three block locations, triggers heartbeats/block reports, lowers replication to one and waits for both active and standby location counts, then raises replication back to three and waits again. `testDatanodeRestarts` creates a five-block file with one DN, waits for standby catch-up, stops the DN, manually notices it dead on both NNs, verifies the active has five under-replicated blocks while the standby has zero needed-replication queue entries, confirms standby block locations are empty, restarts the DN, waits for first block reports, and confirms both NNs report healthy state and standby locations return.

State and persistence behavior: standby state includes block-location maps and DataNode liveness derived from reports, but not active scheduling queues. Replication-factor edits and DataNode restart reports update observable standby read results.

Dependencies and integration points: integrates block reports, heartbeats, replication work computation, standby reads, NameNode adapter block-location calls, and DataNode lifecycle controls.

Risks and test signals: risks include standby stale block locations, slow or missing DataNode re-registration, standby incorrectly managing under-replication queues, and failover to a cold standby. Signals are exact replica-count polling, under-replicated count differences between active and standby, and block-location length changes from one to zero and back to one.
