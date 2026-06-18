<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java

## Purpose

`BlockRecoveryCommand` tells a DataNode to act as primary for lease/block recovery. It carries recovering blocks, their locations, and the new generation stamp or copy-on-truncate target block.

## Important APIs and types

- Extends `DatanodeCommand` with action `DatanodeProtocol.DNA_RECOVERBLOCK`.
- `RecoveringBlock` extends `LocatedBlock` and adds `newGenerationStamp` plus optional `recoveryBlock`.
- `RecoveringStripedBlock` adds block indices and EC policy and overrides `isStriped`.
- Constructors create empty, capacity-sized, or collection-backed commands.
- `add` appends a recovering block.

## Control flow

The NameNode enqueues recovery commands on DataNode heartbeats. The receiving DataNode coordinates with listed locations and uses the recovery id/new generation stamp to finalize block recovery. Copy-on-truncate recovery uses `getNewBlock`.

## State and persistence behavior

The command is a transport DTO. Persistent effects happen in DataNode storage and NameNode block metadata when recovery completes. The backing collection can be externally supplied and mutable.

## Dependencies and integration points

Integrates lease recovery, block management heartbeat handling, inter-DataNode protocol, EC recovery, and protobuf conversion. Depends on `LocatedBlock`, `ExtendedBlock`, `DatanodeInfo`, `Block`, and `ErasureCodingPolicy`.

## Risks and edge cases

Recovery id/new generation stamp correctness is critical to avoid stale writers or inconsistent replicas. Striped recovery must keep block indices aligned with locations. Collection mutability and array references require caller discipline.

## Test signals

`TestHeartbeatHandling`, `TestPendingRecoveryBlocks`, `TestInterDatanodeProtocol`, lease recovery tests, truncate tests, and `TestPBHelper.testConvertRecoveringBlock` provide coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/protocol/BlockRecoveryCommand.java -->
