<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java

## Purpose

`OutOfLegacyGenerationStampsException` is the specific failure raised when the NameNode exhausts the reserved V1 legacy generation-stamp range.

## Important APIs and types

The class extends `IOException`, has a stable `serialVersionUID`, and exposes a no-argument constructor with the fixed message `Out of V1 (legacy) generation stamps`.

## Control flow

There is no internal control flow. The exception is thrown by generation-stamp allocation code when legacy block compatibility space is unavailable.

## State and persistence behavior

The class has no mutable state beyond inherited exception message/cause fields. It is not persisted directly, but the condition reflects exhaustion of namespace-wide generation-stamp state.

## Dependencies and integration points

It is part of the blockmanagement package and integrates with BlockIdManager/generation-stamp allocation paths that distinguish legacy and current generation-stamp spaces.

## Risks and edge cases

The fixed message gives little context about the current counter value or namespace state. Callers should catch it only where a meaningful upgrade or allocation failure response can be produced.

## Test signals

Allocation tests should force the legacy generation-stamp cursor to the reserved limit and assert this exact exception type is raised without advancing into non-legacy space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/OutOfLegacyGenerationStampsException.java -->
