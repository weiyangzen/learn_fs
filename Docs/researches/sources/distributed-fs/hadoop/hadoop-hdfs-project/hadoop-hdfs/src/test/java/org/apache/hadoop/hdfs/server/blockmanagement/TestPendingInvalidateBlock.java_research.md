# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/blockmanagement/TestPendingInvalidateBlock.java

## Purpose
`TestPendingInvalidateBlock` verifies delayed block deletion accounting after namenode startup and for unknown blocks reported by datanodes shortly after restart. It also checks client protocol compatibility for the pending-deletion stats index.

## Important APIs, Types, and Functions
The test uses `MiniDFSCluster`, `DistributedFileSystem`, `InvalidateBlocks`, `Whitebox`, Mockito spies, `DataNodeTestUtils.triggerBlockReport`, `DFSClient.getStateByIndex` via reflection, and `ClientProtocol.GET_STATS_PENDING_DELETION_BLOCKS_IDX`. Helpers are `setUp`, `tearDown`, `waitForReplication`, and `waitForNumPendingDeletionBlocks`.

## Control Flow
Setup configures small block size, five-second startup block-deletion delay, short block-report and heartbeat intervals, and a two-datanode cluster. `testPendingDeletion` creates a replicated file, restarts the namenode, spies `InvalidateBlocks` to force a deletion delay, deletes the file, waits for two pending deletion blocks, then removes the delay and waits for zero. It also invokes `DFSClient.getStateByIndex` for valid and invalid stats indices. `testPendingDeleteUnknownBlocks` creates five files, stops all datanodes, deletes two files, restarts the namenode with delayed invalidation, restarts datanodes, triggers block reports, observes four pending deletions, then restarts the namenode and waits for pending deletion to clear.

## State and Persistence Behavior
State includes persisted file/block metadata across namenode restart, invalidation delay timestamps, pending deletion counters in the namesystem and client stats, and unknown block reports from datanodes.

## Dependencies and Integration Points
The test integrates filesystem delete, namenode restart, block reports, datanode restart, invalidation queue delay logic, client stats compatibility, and white-box block-manager state replacement.

## Risks and Edge Cases
Covered risks include deleting blocks too early during startup, under-reporting pending deletions to clients, mishandling unknown blocks in early block reports, and invalid stats index behavior.

## Test Signals
Assertions verify blocks total is zero or three as expected, pending deletion counts on namesystem and DFS client, block deletion start time after NN start time, valid stats index returning zero after drain, invalid stats index returning -1, and pending unknown deletions clearing after restart.
