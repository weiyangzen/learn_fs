# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/sps/BlockStorageMovementAttemptedItems.java

## Purpose

`BlockStorageMovementAttemptedItems` tracks files whose block movement commands have been submitted to DataNodes. It watches for reported block movement completions, removes finished block targets, and requeues timed-out or completed files for another SPS policy-satisfaction check.

## Important APIs, Types, And Functions

Important state includes `storageMovementAttemptedItems`, `scheduledBlkLocs`, `movementFinishedBlocks`, monitor flags/thread, timeouts, the needed queue, context, and service. Key methods are `add`, `notifyReportedBlock`, `matchesReportedBlock`, `start`, `stop`, `stopGracefully`, `blocksStorageMovementUnReportedItemsCheck`, `blockStorageMovementReportedItemsCheck`, getters for tests, and `clearQueues`.

## Control Flow

SPS calls `add` with assigned blocks and target storage-node pairs. When a DataNode reports a block on a target storage type, `notifyReportedBlock` checks the scheduled locations, removes the matching pair, calls `context.notifyMovementTriedBlocks`, and when all target pairs for the block report, enqueues the block into `movementFinishedBlocks` and removes it from `scheduledBlkLocs`. The monitor thread periodically drains finished blocks and removes them from attempted file records; when a file has no remaining blocks, it adds an `ItemInfo` with incremented retry count to `BlockStorageMovementNeeded`. The same monitor also requeues attempted items whose last attempt/report time exceeds `selfRetryTimeout`.

## State And Persistence Behavior

All state is in-memory and cleared on stop. No attempted movement state is persisted across NameNode restart; SPS relies on xAttrs/queues and later scans to recover work. Timeouts are configured from SPS recheck and self-retry configuration keys.

## Dependencies And Integration Points

It depends on `SPSService`, `Context`, `BlockStorageMovementNeeded`, `StoragePolicySatisfier.AttemptedItemInfo`, `StorageTypeNodePair`, HDFS `Block`, `DatanodeInfo`, `StorageType`, and Hadoop `Daemon`. It is central to feedback between DataNode reports and SPS retry scheduling.

## Risks And Edge Cases

`matchesReportedBlock` iterates and removes from a set during enhanced-for iteration, then returns immediately; this relies on no further iterator use after removal. A block can be reported by one target but not all targets, leaving the file attempted until timeout. Completed files are requeued for policy recheck rather than declared done, so retry counts must not be interpreted as only failures. The monitor exits on `IOException`, which can stop further attempt processing. Synchronization is split between attempted list, scheduled map, and finished queue.

## Test Signals

Tests should cover successful block reports for all target pairs, partial reports followed by timeout, unknown reports, duplicate reports, monitor start/stop/interrupt, IOException from reported-item checks, configured timeouts, queue clearing, and retry count increments for both timeout and finished-block requeue paths.
