<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java

## Purpose

`BlockECReconstructionCommand` instructs a DataNode to reconstruct missing internal blocks in an erasure-coded striped block group and send reconstructed data to target storages.

## Important APIs and types

- Extends `DatanodeCommand`.
- Holds `Collection<BlockECReconstructionInfo>`.
- `BlockECReconstructionInfo` carries the block group, source DataNodes, target DataNodes/storage ids/storage types, live block indices, excluded reconstructed indices, and `ErasureCodingPolicy`.
- Constructors accept either target `DatanodeStorageInfo[]` or already-converted arrays.

## Control flow

The NameNode builds reconstruction tasks from block-management state and sends them to a DataNode. The receiver pulls from source nodes and reconstructs missing blocks based on live indices and EC policy. `toString` logs all tasks for diagnostics.

## State and persistence behavior

The command is an RPC DTO. It contains arrays and collections by reference and does not persist state itself. Persistent effects occur when reconstruction succeeds and DataNodes report the new replicas.

## Dependencies and integration points

Integrates EC block management, DataNode reconstruction workers, `DatanodeStorageInfo` conversion helpers, protobuf conversion, and `ErasureCodingPolicy`.

## Risks and edge cases

Array lengths and index semantics are critical; live indices, excluded indices, sources, and targets must match the EC policy. `excludeReconstructedIndices` is not null-normalized, unlike `liveBlockIndices`. Mutable arrays can be changed after construction if callers retain references.

## Test signals

`TestPBHelper`, `TestDatanodeManager`, striped reconstruction tests, rack-awareness reconstruction tests, and EC corruption tests cover conversion and scheduling. Tests should include multiple missing blocks, target storage metadata, and null/empty index arrays.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockECReconstructionCommand.java -->
