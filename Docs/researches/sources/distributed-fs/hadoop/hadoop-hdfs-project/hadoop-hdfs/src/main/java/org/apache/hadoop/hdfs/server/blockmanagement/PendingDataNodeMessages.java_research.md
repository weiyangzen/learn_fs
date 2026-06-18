<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java

## Purpose

`PendingDataNodeMessages` queues block reports or incremental block messages that a standby NameNode receives before namespace state is ready to process them. It prevents early or future-state DataNode messages from being lost during HA standby processing.

## Important APIs and types

The main state is `Map<Block, Queue<ReportedBlockInfo>> queueByBlockId` plus a total `count`. `ReportedBlockInfo` stores the copied `Block`, `DatanodeStorageInfo`, and reported `ReplicaState`. APIs include `enqueueReportedBlock`, `removeQueuedBlock`, `removeAllMessagesForDatanode`, `takeBlockQueue`, `takeAll`, `count`, and `toString`.

## Control flow

Enqueue normalizes striped internal block IDs to their block-group ID key while preserving the reported block in the queued record. Removal by queued block similarly normalizes striped IDs, removes all reports from the same storage, and drops empty queues; this is explicitly to avoid an older non-future report being processed after failover. `takeBlockQueue` and `takeAll` transfer ownership to callers and decrement or reset `count`.

## State and persistence behavior

State is in-memory standby-only buffering. There is no synchronization in this class, so callers must provide the surrounding NameNode locking or single-threading discipline.

## Dependencies and integration points

It depends on `Block`, `BlockIdManager`, `DatanodeDescriptor`, `DatanodeStorageInfo`, and `HdfsServerConstants.ReplicaState`. It integrates with standby block report and failover processing.

## Risks and edge cases

The `count` field must stay aligned with queue mutations; bugs can skew metrics and capacity sizing. `removeAllMessagesForDatanode` replaces queue values while iterating map entries but does not remove now-empty block keys. Block key normalization for striped blocks is essential; missing it would split messages for a single block group.

## Test signals

Tests should cover contiguous and striped enqueue/take, same-storage replacement/removal, DataNode-wide removal, count correctness, empty queue cleanup, and failover replay order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/PendingDataNodeMessages.java -->
