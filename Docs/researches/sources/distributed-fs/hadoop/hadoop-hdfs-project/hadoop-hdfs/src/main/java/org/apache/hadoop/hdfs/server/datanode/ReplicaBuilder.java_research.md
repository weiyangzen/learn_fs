<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBuilder.java

## Purpose

`ReplicaBuilder` centralizes construction of `ReplicaInfo` implementations. It maps a requested `ReplicaState` plus storage type and optional source replica into the correct local or provided replica class.

## Important APIs, Types, And Functions

- Fluent setters configure block id, generation stamp, length, volume, directory, reservation, writer thread, recovery id, `Block`, URI, `Configuration`, `FileRegion`, `FileSystem`, `PathHandle`, prefix/suffix, and last partial chunk checksum.
- `buildLocalReplicaInPipeline()` creates RBW or temporary in-pipeline replicas.
- `build()` dispatches to provided or local construction based on `volume.getStorageType() == StorageType.PROVIDED`.
- Private builders create `FinalizedReplica`, `ReplicaBeingWritten`, `LocalReplicaInPipeline`, `ReplicaWaitingToBeRecovered`, `ReplicaUnderRecovery`, and `FinalizedProvidedReplica`.

## Control Flow

The state drives construction. Copy construction is allowed only when `fromReplica` already has the expected state, except RUR construction wraps a finalized/RBW/RWR source with a recovery id. Provided volumes support only finalized provided replicas and require either a `FileRegion`, direct URI, or path prefix plus suffix.

## State And Persistence

The builder is mutable and accumulates construction parameters until `build()` is called. It does not persist data itself. Resulting local replicas point at block/meta files and directories; provided replicas point at remote regions.

## Dependencies And Integration Points

It is the factory bridge between dataset loading, recovery, write pipeline setup, provided storage, and the concrete replica class hierarchy. It depends on `StorageType`, `FsVolumeSpi`, `Block`, `FileRegion`, and Hadoop filesystem handles.

## Risks And Edge Cases

Many fields are optional and only validated in the path that uses them. Missing writer threads for some block-based in-pipeline constructors, incompatible `fromReplica` states, missing provided-location metadata, or null volumes can fail late. Provided replicas reject all non-finalized states.

## Test Signals

Tests should cover every state, copy-construction compatibility, RUR recovery-id wrapping, provided replica construction by URI, prefix/suffix, and `FileRegion`, plus failure cases for invalid state/field combinations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/ReplicaBuilder.java -->
