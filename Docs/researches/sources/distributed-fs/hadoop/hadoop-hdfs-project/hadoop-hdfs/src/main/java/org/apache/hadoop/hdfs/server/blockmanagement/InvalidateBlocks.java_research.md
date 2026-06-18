# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/InvalidateBlocks.java

## Purpose

`InvalidateBlocks` tracks blocks that should be deleted from datanodes and batches them into invalidation work sent on heartbeat. It maintains separate queues for contiguous replicated blocks and striped erasure-coded blocks so counts and limits can be managed accurately.

## Important APIs, Types, and State

State includes `nodeToBlocks`, `nodeToECBlocks`, `LongAdder numBlocks`, `LongAdder numECBlocks`, `blockInvalidateLimit`, `BlockIdManager`, `pendingPeriodInMs`, and `startupTime`. Methods include `numBlocks()`, `getBlocks()`, `getECBlocks()`, `contains()`, `add()`, `remove(dn)`, `remove(dn, block)`, `dump()`, `getDatanodes()`, `getInvalidationDelay()`, `invalidateWork(DatanodeDescriptor)`, and `clear()`.

## Control Flow

`add()` selects the replicated or striped map using `BlockIdManager.isStripedBlock()`, creates a per-datanode `LightWeightHashSet` if needed, inserts the block, updates the appropriate counter, and optionally logs. `contains()` verifies block presence and generation stamp equality. `remove()` variants delete all work for a datanode or a specific block, decrement counters, and remove empty per-node entries.

`invalidateWork()` first enforces the startup deletion delay. If the delay has not elapsed, it returns null and logs that deletion is delayed. Otherwise it polls up to `blockInvalidateLimit` replicated blocks first, then uses remaining capacity for EC blocks. If any blocks are selected, it removes empty node entries and enqueues the blocks into the descriptor's invalidate set via `addBlocksToBeInvalidated()`. The actual protocol command is later emitted by `DatanodeManager.handleHeartbeat()`.

## State and Persistence Behavior

Invalidation queues are runtime NameNode state derived from block deletion, over-replication, and block-report reconciliation. They are not persisted here. The startup pending period protects against deleting replicas before stale storage and block reports have been reconciled after NameNode startup.

## Dependencies and Integration Points

It depends on `BlockIdManager`, `DatanodeInfo`, `DatanodeDescriptor`, `LightWeightHashSet`, NameNode block-state logging, and `DFS_NAMENODE_STARTUP_DELAY_BLOCK_DELETION_SEC_KEY`. `BlockManager` computes invalidation work and `DatanodeManager` sends the resulting commands.

## Risks and Edge Cases

Important risks include deleting blocks during startup before block reports establish freshness, generation-stamp mismatches, and starving EC invalidations if replicated invalidations constantly fill the limit. The class is synchronized for map/counter consistency, while `LongAdder` is used for counters. `dump()` can output both maps for metasave diagnostics.

## Test Signals

`TestComputeInvalidateWork`, `TestPendingInvalidateBlock`, `TestPendingDataNodeMessages`, `TestBlockManager`, `TestDeleteRace`, and startup tests are relevant. Coverage should assert startup delay behavior, generation-stamp-aware contains, replicated-before-EC batching, per-node cleanup, and command handoff to `DatanodeDescriptor`.
