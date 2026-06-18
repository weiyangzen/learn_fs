<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaUnderRecovery.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaUnderRecovery.java

## Purpose

`ReplicaUnderRecovery` wraps a local finalized, RBW, or RWR replica while lease/block recovery is in progress. It records a recovery id, which is the generation stamp the replica should be bumped to after successful recovery.

## Important APIs, Types, And Functions

- Constructor validates the source state is `FINALIZED`, `RBW`, or `RWR`, then copies block metadata and keeps the original local replica.
- `getState()` returns `ReplicaState.RUR`.
- `setRecoveryID(long)` only accepts strictly larger recovery ids, allowing newer recovery attempts to preempt older ones.
- Block mutators and `setVolume()` update both wrapper and original replica.
- `createInfo()` returns `ReplicaRecoveryInfo` based on the original replica's block id, bytes on disk, generation stamp, and state.

## Control Flow

Recovery code wraps a valid original replica, compares or advances recovery ids, then updates block id, generation stamp, length, location, and volume through the wrapper. Reads of visible length and bytes on disk delegate to the original.

## State And Persistence

The wrapper stores `original` and `recoveryId`. Persistent files remain owned by the original local replica. Metadata updates are mirrored to the original to keep the in-memory wrapper and local storage representation coherent.

## Dependencies And Integration Points

It depends on `LocalReplica`, `ReplicaState`, `FsVolumeSpi`, `StorageLocation`, and `ReplicaRecoveryInfo`. `ReplicaBuilder.buildRUR()` constructs it from an existing replica and recovery id.

## Risks And Edge Cases

The constructor casts the source to `LocalReplica`; provided replicas are not supported. Lower or equal recovery ids are rejected. Any method that updates wrapper but not original would corrupt recovery state, so the mirrored overrides are important.

## Test Signals

Tests should cover valid and invalid source states, recovery-id monotonicity, delegation of visible/disk lengths, mirrored block-field updates, volume/location updates, copy construction, and generated recovery info.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaUnderRecovery.java -->
