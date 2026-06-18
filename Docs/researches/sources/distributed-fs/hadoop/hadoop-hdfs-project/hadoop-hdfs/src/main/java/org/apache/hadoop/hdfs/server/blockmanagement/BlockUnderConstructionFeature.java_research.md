# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockUnderConstructionFeature.java

## Purpose

`BlockUnderConstructionFeature` stores mutable state for a block that is still being written, appended, truncated, committed, or recovered. It is usually attached to the last block of an open file.

## Important APIs and types

- Constructor records `BlockUCState` and expected target storages.
- `setExpectedLocations`, `getExpectedStorageLocations`, iterator access, `getBlockIndices`, and `getBlockIndicesForSpecifiedStorages` manage expected replicas.
- `updateStorageScheduledSize` adjusts scheduled-block counts for partial striped blocks.
- State APIs include `getBlockUCState`, `setBlockUCState`, `commit`, `getBlockRecoveryId`, `getTruncateBlock`, and `setTruncateBlock`.
- `getStaleReplicas` identifies replicas with wrong generation stamps.
- `initializeBlockRecovery` selects a primary datanode and queues recovery work.
- `addReplicaIfNotPresent` incorporates reported replicas and storage moves.

## Control flow

Expected locations are built from non-null target storages. For striped blocks, each expected replica uses a block ID offset so internal block indices map to storages. Recovery sets state to `UNDER_RECOVERY`, records the recovery ID, optionally rotates primary selection, resets `chosenAsPrimary` once all live replicas have been tried, and chooses the live replica with the most recent heartbeat as primary. It then adds the block to that datanode's recovery queue.

Reported replicas update an existing expected storage by generation stamp, replace an entry if the same datanode reports the block on a different storage, or append a new replica entry. String helpers expose full or concise state for logs.

## State and persistence behavior

The class holds under-construction state in memory as part of `BlockInfo`. It includes state, expected replicas, primary index, recovery ID, and optional truncate block. Durable representation is handled by NameNode metadata serialization outside this class.

## Dependencies and integration points

It integrates with `BlockInfo`, `BlockInfoStriped`, `ReplicaUnderConstruction`, datanode storage scheduling, lease recovery, NameNode block state logs, block type handling, and replica states.

## Risks and edge cases

The constructor assertion checks `getBlockUCState()` before assigning the constructor state, so it relies on default null behavior and does not validate the passed state directly. Iterators are explicitly not thread-safe and require external FSNamesystem locking. Recovery with no replicas logs and sets primary index to -1. Partial striped block scheduled-size adjustments must match block index math.

## Test signals

Tests should cover replicated and striped expected-location creation, null targets, block index calculation, scheduled-size decrement for short stripes, recovery primary rotation, stale replica detection, reported storage replacement, append of unexpected replicas, and no-replica recovery behavior.
