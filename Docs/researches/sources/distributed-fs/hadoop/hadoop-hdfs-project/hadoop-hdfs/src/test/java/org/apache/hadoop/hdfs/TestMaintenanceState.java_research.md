# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/TestMaintenanceState.java

## Purpose
This slow HDFS integration test validates DataNode maintenance admin states for replicated blocks. It covers configuration bounds, transitions among `NORMAL`, `ENTERING_MAINTENANCE`, `IN_MAINTENANCE`, `DECOMMISSION_INPROGRESS`, and `DECOMMISSIONED`, read-location filtering, replication repair, expiration, dead-node handling, restart behavior, write allocation, invalidation, open-file close, and `DFSAdmin -report` output.

## Important APIs, Types, And Functions
The class extends `AdminStatesBaseTest` and relies on its cluster, host-file, node-state, and file-writing helpers. Key tests include `testMaintenanceMinReplConfigRange`, `testTakeNodeOutOfEnteringMaintenance`, `testPutDeadNodeToMaintenance`, `testExpectedReplications`, `testFileBlockReplicationAffectingMaintenance`, `testTransitionToDecommission`, `testMultipleNodesMaintenance`, `testChangeReplicationFactors`, `testTakeDeadNodeOutOfMaintenance`, `testWithNNAndDNRestart`, `testWriteAfterMaintenance`, `testInvalidation`, `testFileCloseAfterEnteringMaintenance`, and `testReportMaintenanceNodes`. Shared verification is in `checkFile`, `checkWithRetry`, `getFirstBlockFirstReplicaUuid`, and `getFirstBlockReplicasDatanodeInfos`.

## Control Flow
Most tests start a `MiniDFSCluster`, create a file with a chosen replication factor, select the first replica location, write host-manager maintenance/decommission state through base helpers, refresh the NameNode, and wait for block placement or admin-state convergence. Verification opens a raw `HdfsDataInputStream`, inspects `LocatedBlock` locations exposed to readers, and separately walks `BlockManager.getStorages` to confirm maintenance replicas remain in the block map while being hidden from client reads. Restart scenarios stop DataNodes, restart NameNodes, then validate that block maps and replica counts converge again.

## State And Persistence
State under test is NameNode-maintained DataNode admin state, maintenance expiration timestamps, live/dead maintenance counters in `FSNamesystem`, block-manager storage membership, pending/under-replicated counts, and file replication state. Persistence-sensitive tests verify maintenance replicas across NameNode restart, DataNode restart, and invalidation decisions. The test also confirms that maintenance nodes are excluded from new block allocation and invalidation, but their replicas remain accounted where appropriate.

## Dependencies And Integration Points
The file integrates `MiniDFSCluster`, `DFSClient`, `DistributedFileSystem`, `FSNamesystem`, `BlockManager`, `DatanodeStorageInfo`, `NameNodeAdapter`, `DFSAdmin`, combined host-file management, `GenericTestUtils.waitFor`, and HDFS protocol classes such as `DatanodeInfo`, `LocatedBlock`, and `LocatedBlocks`.

## Risks
These tests are race-sensitive because maintenance transitions depend on heartbeat, redundancy, and block-placement timing. `checkWithRetry` catches and ignores exceptions while polling, so persistent failures may surface only as timeout behavior. Tests that change shared configuration call `setup`/`teardown` manually inside helper loops and would be fragile if base-class lifecycle behavior changes. Output redirection in `testReportMaintenanceNodes` is process-global and can interfere with concurrent tests.

## Test Signals
Strong signals are exact live/dead/entering/in-maintenance counters, expected `LocatedBlock` replica counts, absence of maintenance nodes in read locations, presence of maintenance replicas in block-manager storage lists, successful recovery after NN/DN restart, successful close of files whose last-block nodes are entering maintenance, and DFSAdmin report text listing only the requested maintenance categories.
