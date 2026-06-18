# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/datanode/TestBlockRecovery.java

## Purpose
`TestBlockRecovery` is a broad unit and integration suite for DataNode block recovery. It verifies contiguous replica synchronization rules, failure handling before NameNode commit, striped safe-length calculation, lock behavior while stopping writers, and delayed recovery retry behavior.

## Important APIs, Types, and Functions
- `BlockRecoveryWorker`, `RecoveryTaskContiguous`, `RecoveryTaskStriped`, and `BlockRecord` are the main system-under-test types.
- `ReplicaRecoveryInfo` with `ReplicaState` values `FINALIZED`, `RBW`, `RWR`, and `RUR` drives sync-rule coverage.
- `InterDatanodeProtocol#updateReplicaUnderRecovery` and `DatanodeProtocol#commitBlockSynchronization` are key protocol outputs.
- `initRecoveringBlocks`, `initBlockRecords`, and `testSyncReplicas` assemble synthetic recovery tasks.
- `testStopWorker` verifies lockless behavior for `initReplicaRecovery`, `recoverAppend`, and `recoverClose`.
- Static `testRecoveryWithDatanodeDelayed` is reused by `TestBlockRecovery2` to test slow commit synchronization in a real cluster.

## Control Flow and Behavior
The setup starts a standalone DataNode pointed at a mocked NameNode. Registration and heartbeats are mocked to make the BPOfferService see an active NameNode. The test wraps the DataNode with a spy and constructs a `BlockRecoveryWorker`.

Replica-state tests call `syncBlock` with two mocked inter-DataNode records and assert which replicas are updated and to what length. Finalized replicas must agree on length; RBW/RWR combinations choose the finalized length, RBW length, or minimum length according to recovery rules. Failure-injection tests make `initReplicaRecovery` throw `RecoveryInProgressException` or `IOException`, return zero-length finalized replicas, return RUR replicas, or fail `updateReplicaUnderRecovery`, then assert sync or commit behavior.

Striped recovery coverage constructs `RecoveringStripedBlock` and verifies `getSafeLength` over several block-length suites aligned with the default EC policy. Lock tests create a slow writer owning a replica and then run recovery operations that interrupt and join that writer; while join is in progress the main test calls `getReplicaString`, proving dataset locks are not held while waiting.

## State and Persistence
The standalone DataNode uses a real local `DATA_DIR` that is deleted before and after each test. Tests create RBW replicas and replica streams in the dataset. In MiniDFSCluster integration paths, actual HDFS files, leases, and block recovery timeouts are used.

## Dependencies and Integration Points
This suite integrates DataNode storage (`FsDatasetSpi`), block-pool services, NameNode protocol mocks, recovery protocol classes, replica output streams, checksums, EC policy helpers, MiniDFSCluster, DFS clients, leases, and `GenericTestUtils` fault helpers. It is one of the main tests protecting the DataNode-NameNode recovery protocol contract.

## Risks and Edge Cases
Covered risks include inconsistent finalized replica lengths, skipping stale non-finalized replicas, zero-length recovery commits, all-DataNode failure messages, RUR-only records, mismatched recovery IDs, failed replica updates, avoiding NameNode commit when sync fails, safe-length math for striped block groups, lock contention while interrupting slow writers, and recovery delays exceeding heartbeat intervals. Some assertions only check message prefixes by calling `startsWith` without asserting the result, so those branches may be weaker than intended.

## Test Signals
Signals include Mockito verification of `updateReplicaUnderRecovery` calls and lengths, `commitBlockSynchronization` arguments, absence of commit calls on failure paths, expected exceptions, striped safe-length equality, successful concurrent lock access during writer joins, and real-cluster completion of delayed recovery.
