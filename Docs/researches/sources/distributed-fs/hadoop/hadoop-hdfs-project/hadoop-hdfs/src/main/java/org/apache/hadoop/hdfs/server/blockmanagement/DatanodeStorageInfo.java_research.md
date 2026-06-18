# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/DatanodeStorageInfo.java

## Purpose

`DatanodeStorageInfo` represents one storage volume reported by a datanode. It stores storage identity, type, state, capacity metrics, block-list membership, and block-report freshness flags. It is the link between `DatanodeDescriptor` and `BlockInfo` storage lists.

## Important APIs, Types, and State

Static conversion helpers produce datanode arrays, descriptor arrays, storage IDs, and storage types from storage arrays/lists. Instance state includes parent `DatanodeDescriptor`, `storageID`, `storageType`, `state`, capacity/usage metrics, `blockList` head, `numBlocks`, block-report count, `hasReceivedBlockReport`, `heartbeatedSinceFailover`, and `blockContentsStale`.

Important methods include `receivedHeartbeat()`, `receivedBlockReport()`, `markStaleAfterFailover()`, `addBlock()`, `removeBlock()`, `insertToList()`, `getBlockIterator()`, `moveBlockToHead()`, `updateState()`, `toStorageReport()`, and scheduled-block increment/decrement helpers.

## Control Flow

Heartbeats update storage state and metrics and mark `heartbeatedSinceFailover`. A block report clears `blockContentsStale` only after a heartbeat has occurred since failover, then increments block-report count. `addBlock()` handles the case where a block is already associated with a different storage on the same datanode by removing it from the old storage and returning `REPLACED`; if already on this storage, it returns `ALREADY_EXIST`. Otherwise it attaches the block to the head of the storage's linked block list.

`removeBlock()` removes the block from both the linked list and the block's storage membership, decrementing `numBlocks` only when storage removal succeeds. `BlockIterator` traverses the per-storage linked list through `BlockInfo` next pointers.

## State and Persistence Behavior

The object is in-memory state reconstructed from datanode storage reports and block reports. `blockContentsStale` protects invalidation safety after startup/failover: while stale, replicas on the storage should not be trusted for deletion decisions. Capacity metrics mirror the most recent `StorageReport`.

## Dependencies and Integration Points

It integrates with `DatanodeDescriptor`, `BlockInfo`, `DatanodeStorage`, `StorageReport`, storage policies, block placement, heartbeat handling, and invalidation/reconstruction flows. `BlockManager` and block-report processing rely on accurate block list membership.

## Risks and Edge Cases

Block-list consistency is critical. Moving a block between storages on the same datanode must remove old membership before insertion. Failed storage can still contain blocks until heartbeat checks remove associated blocks. Stale-after-failover logic must not be bypassed, or invalidations may delete replicas whose state the NameNode has not yet revalidated.

## Test Signals

Relevant tests include `TestDatanodeDescriptor`, `TestBlockInfo`, `TestNameNodePrunesMissingStorages`, `TestBlockReportLease`, `TestProvidedStorageMap`, and block report variation tests. Good coverage verifies replacement between storages, stale content flags across failover, failed storage block removal, and storage report conversion.
