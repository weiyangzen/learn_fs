# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/ExcessRedundancyMap.java

## Purpose

`ExcessRedundancyMap` tracks block replicas that the NameNode has selected as excess on specific datanodes. It prevents duplicate excess markings and lets block-management code query or remove excess state by datanode UUID and block.

## Important APIs, Types, and State

State is a synchronized `Map<String, LightWeightHashSet<Block>>` keyed by datanode UUID plus an `AtomicLong size` for total excess entries. Methods include `size()`, `clear()`, `contains(DatanodeDescriptor, BlockInfo)`, `add(DatanodeDescriptor, BlockInfo)`, `remove(DatanodeDescriptor, BlockInfo)`, `getExcessRedundancyMap()`, and testing size lookup.

Nested `ExcessBlockInfo` extends `Block` and stores the original `BlockInfo` plus a monotonic timestamp updated at construction or through `setTimeStamp()`.

## Control Flow

`add()` creates a per-datanode set if needed, wraps the block in `ExcessBlockInfo`, and increments total size only if the set did not already contain an equivalent block. `remove()` deletes the block, decrements size, logs the change, and removes the per-datanode set when empty. `contains()` uses block equality in the per-datanode set.

## State and Persistence Behavior

The map is runtime-only. It reflects current excess-replica decisions and is cleared or rebuilt by block-management processing. The timestamp records when an excess decision was made, which can support aging or diagnostics by consumers.

## Dependencies and Integration Points

It integrates with `BlockManager` over-replication handling, `NameNode.blockStateChangeLog`, `LightWeightHashSet`, `DatanodeDescriptor`, and `BlockInfo`. It is thread-safe through synchronized methods even though the size counter is atomic.

## Risks and Edge Cases

The main risk is stale entries after block deletion, replica movement, or datanode removal. Consumers must call `remove()` or `clear()` appropriately. `getExcessRedundancyMap()` exposes the mutable map under synchronization only for the call; external mutation would be risky if used outside trusted package code.

## Test Signals

Over-replication tests such as `TestOverReplicatedBlocks`, `TestBlockManager`, `TestNodeCount`, and pending reconstruction/invalidation tests can reveal incorrect excess tracking. Unit coverage should assert add idempotency, remove cleanup of empty datanode sets, and total size consistency.
