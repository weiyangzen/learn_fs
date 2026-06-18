# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/ha/TestStandbyBlockManagement.java

Purpose: ensures standby and observer NameNodes ingest block state but do not perform active-only block management work such as invalidation or redundant replica processing.

Important APIs and types: `MiniDFSCluster`, `HAUtil.setAllowStandbyReads`, `BlockManagerTestUtil.computeAllPendingWork`, `BlockManager.getPendingDeletionBlocksCount`, `BlockManager.getExcessBlocksCount`, `DFSTestUtil.waitReplication`, and NameNode state assertions.

Control flow: `testInvalidateBlock` creates a two-NN, three-DN HA cluster, writes a file, rolls edits so the standby catches up, deletes the file on the active, computes pending work on the active, rolls edits again, and asserts the standby has zero pending deletion blocks before and after heartbeats/block reports. `testNotHandleRedundantReplica` starts four DNs, confirms active/standby states and empty excess maps, writes a file with replication four, lowers replication to three, waits for standby catch-up and DN deletion reports, and asserts both active and standby have zero excess blocks after the active-driven deletion completes.

State and persistence behavior: deletion and replication-factor edits are tailed by standby, but scheduling deletion and excess-replica bookkeeping must remain active-owned. Standby state should reflect block locations without enqueuing deletion work.

Dependencies and integration points: integrates NameNode block manager queues, DataNode heartbeat/block/deletion reports, HA tailing, replication monitor calculations, and standby reads.

Risks and test signals: risks include standby issuing invalidations, accumulating excess replica state, or double-processing block-management actions after failover. Signals are exact zero counts for pending deletion and excess blocks around triggered reports and replication changes.
