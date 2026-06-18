# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/LocatedStripedBlock.java

## Purpose
`LocatedStripedBlock` specializes `LocatedBlock` for erasure-coded striped block groups. Each storage location is associated with a block index inside the group and may have an individual block token.

## APIs and Behavior
The constructor delegates common block-location state to `LocatedBlock`, copies the supplied indices array, and initializes one empty token per index. It overrides `isStriped()` and `getBlockType()` to report striped blocks. Getters/setters expose block indices and per-internal-block tokens; `toString()` includes indices.

## State, Dependencies, and Integration
The class is mutable for indices and tokens. It depends on `StorageType`, `DatanodeInfo`, `Token<BlockTokenIdentifier>`, and `BlockType.STRIPED`. It is produced by NameNode block-location conversion for EC files and consumed by client read reconstruction logic.

## Risks and Test Signals
`setBlockIndices()` stores the provided array directly, unlike the constructor copy. Token array length must stay aligned with indices and locations. Tests should cover defensive copying, token/index alignment, block type reporting, toString diagnostics, and EC read-path conversion to user-facing block locations.
