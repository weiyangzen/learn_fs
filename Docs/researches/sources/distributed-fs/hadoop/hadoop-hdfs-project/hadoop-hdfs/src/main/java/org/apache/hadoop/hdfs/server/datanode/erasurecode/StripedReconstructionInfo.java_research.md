<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructionInfo.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructionInfo.java

## Purpose

`StripedReconstructionInfo` is the immutable data carrier describing a striped block reconstruction or checksum reconstruction task: block group, EC policy, source indices and datanodes, target indices or target datanodes, target storage, and exclusions.

## Important APIs, Types, And Functions

- Public constructor supports checksum-style reconstruction with explicit target indices and no target datanodes.
- Package-private constructor supports NameNode reconstruction commands with target datanodes, storage types, storage ids, and excluded reconstructed indices.
- Getters expose block group, policy, live indices, sources, target indices, targets, target storage types/ids, and exclusions.

## Control Flow

The class has no behavior beyond construction and getters. `ErasureCodingWorker` builds it from `BlockECReconstructionInfo`; reconstructor, reader, and writer classes then consume the fields to compute block lengths, source readers, and target writers.

## State And Persistence

All fields are final references. The class does not copy arrays, so callers must treat passed arrays as immutable after construction. It persists nothing.

## Dependencies And Integration Points

It binds protocol-level `ExtendedBlock`, `ErasureCodingPolicy`, `DatanodeInfo`, and `StorageType` data to the DataNode EC reconstruction implementation.

## Risks And Edge Cases

Array length consistency is mostly validated later in reader/writer constructors. Mutating arrays after construction can corrupt reconstruction. Some fields are null depending on reconstruction mode, so consumers must use the correct constructor path.

## Test Signals

Tests should cover both construction modes, getter identity/contents, null field expectations, exclusion propagation, and validation in downstream reader/writer constructors for mismatched arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/erasurecode/StripedReconstructionInfo.java -->
