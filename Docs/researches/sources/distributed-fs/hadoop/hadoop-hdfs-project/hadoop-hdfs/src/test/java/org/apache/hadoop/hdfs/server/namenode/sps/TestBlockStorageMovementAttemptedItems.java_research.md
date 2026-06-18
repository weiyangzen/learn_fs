# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/test/java/org/apache/hadoop/hdfs/server/namenode/sps/TestBlockStorageMovementAttemptedItems.java

## Purpose
`TestBlockStorageMovementAttemptedItems` verifies the SPS attempted-items monitor that tracks block storage movement attempts, DataNode reports, and retry scheduling for partial or timed-out movements.

## Important APIs, Types, and Functions
The test uses `BlockStorageMovementAttemptedItems`, `BlockStorageMovementNeeded`, `StoragePolicySatisfier`, `ExternalSPSContext`, `ItemInfo`, `Block`, `DatanodeInfo`, `StorageType`, and `StoragePolicySatisfier.StorageTypeNodePair`. Mockito stubs the `Context` as running, not in safe mode, and with files existing. `checkItemMovedForRetry` polls the needed queue until an item is requeued.

## Control Flow
Setup constructs a real `StoragePolicySatisfier` and attempted/needed queues around a mocked external context. Tests add attempted block maps, optionally notify finished movement reports, and then check finished-report queue counts, attempted item counts, or retry movement into `BlockStorageMovementNeeded`. One test starts the monitor thread so reported and unreported checks run asynchronously; another invokes `blocksStorageMovementUnReportedItemsCheck` and `blockStorageMovementReportedItemsCheck` manually after timeout ordering; the final test verifies a reported block alone does not requeue when the attempted queue is not processed.

## State and Persistence Behavior
The state is in-memory queue/monitor state: attempted item lists, movement finished block reports, and retry queue entries. There is no disk persistence.

## Dependencies and Integration Points
This tests SPS internal coordination between attempted movement tracking and the needed queue that schedules future work. It depends on monotonic time, self-retry timeouts, and DataNode/storage-type matching.

## Risks and Edge Cases
Risks include partial movement being treated as complete, reports being dropped, items never requeued after timeout, race/order differences between reported-check and unreported-check paths, and monitor threads leaking across tests. Teardown stops the monitor both normally and gracefully.

## Test Signals
Signals are movement finished block counts, attempted item counts, and successful/unsuccessful polling for a requeued `ItemInfo` in `BlockStorageMovementNeeded`.
