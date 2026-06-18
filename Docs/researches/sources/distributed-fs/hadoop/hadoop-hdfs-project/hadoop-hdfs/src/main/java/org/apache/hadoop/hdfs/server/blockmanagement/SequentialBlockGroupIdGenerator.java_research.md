<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java

## Purpose

`SequentialBlockGroupIdGenerator` allocates negative erasure-coded block-group IDs while preserving the low bits reserved for internal block indexes within a group.

## Important APIs and types

It extends `SequentialNumber`, starts at `Long.MIN_VALUE`, and exposes `nextValue`. It uses `BLOCK_GROUP_INDEX_MASK` and `MAX_BLOCKS_IN_GROUP` from `HdfsServerConstants` and checks conflicts through `BlockManager.getStoredBlock`.

## Control flow

`nextValue` advances to the next aligned group boundary by clearing index bits and adding `MAX_BLOCKS_IN_GROUP`. It then probes every possible internal block ID in that group range. If any ID already exists in the block map, it skips the whole group range and retries. If allocation reaches non-negative IDs, it throws to avoid colliding with contiguous blocks.

## State and persistence behavior

The current sequential value is in-memory runtime state inherited from `SequentialNumber` and is initialized/restored by BlockIdManager/namespace loading elsewhere. The method requires an external lock to prevent concurrent ID conflicts.

## Dependencies and integration points

It integrates with BlockManager's block map, EC block ID encoding, and namespace/block ID initialization.

## Risks and edge cases

The collision scan must cover every internal index in the group; otherwise a random legacy block ID could collide with an EC internal block. External locking is required but not enforced in this class. Exhausting negative IDs is fatal.

## Test signals

Tests should cover group-boundary alignment, conflict skipping for each internal index, non-negative exhaustion failure, and concurrent allocation guarded by BlockIdManager locks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/SequentialBlockGroupIdGenerator.java -->
