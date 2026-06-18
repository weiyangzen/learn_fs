<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java

## Purpose

`SequentialBlockIdGenerator` allocates positive contiguous block IDs, starting after the historical reserved range, while skipping conflicts with previously random block IDs.

## Important APIs and types

It extends `SequentialNumber`, defines `LAST_RESERVED_BLOCK_ID` as `2^30`, and exposes `nextValue`. Conflict checking uses `BlockManager.getStoredBlock` and ignores block-map entries whose block collection ID is `INodeId.INVALID_INODE_ID`.

## Control flow

`nextValue` obtains the next sequential number, wraps it in a `Block`, and loops while `isValidBlock` reports a real stored block conflict. It throws if the value wraps negative because negative ID space is reserved for erasure-coded block groups.

## State and persistence behavior

The current counter is runtime namespace state managed externally by BlockIdManager. The generator itself does not persist IDs and relies on external synchronization for uniqueness.

## Dependencies and integration points

It integrates with BlockManager, the block map, INode ID validity, and NameNode block allocation.

## Risks and edge cases

Only valid file-owned block map entries block allocation; invalid collection IDs are skipped. Exhaustion into negative space is fatal. Historical random-ID conflicts should be rare but must be tested because skipping must not allocate an existing block.

## Test signals

Tests should verify initial value, conflict skipping, invalid-inode conflict bypass, negative wrap failure, and lock-protected uniqueness under concurrent allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockIdGenerator.java -->
