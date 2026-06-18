# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/CorruptReplicasMap.java

## Purpose

`CorruptReplicasMap` tracks datanodes that hold corrupt replicas for each block. It lets the NameNode hide corrupt replicas from normal placement accounting and clear corruption once enough good replicas exist or specific reasons are resolved.

## Important APIs and types

- `Reason` enumerates `NONE`, `ANY`, `GENSTAMP_MISMATCH`, `SIZE_MISMATCH`, `INVALID_STATE`, and `CORRUPTION_REPORTED`.
- `addToCorruptReplicasMap` adds or updates a datanode reason for a block.
- `removeFromCorruptReplicasMap` removes an entire block or one datanode entry, optionally matching a reason.
- `getNodes`, `isReplicaCorrupt`, `numCorruptReplicas`, `size`, `getCorruptBlocksSet`, and `getCorruptReason` expose contents.
- `getCorruptBlockIdsForTesting` returns sorted replicated or striped corrupt block IDs within a bounded page.
- `getCorruptBlocks` and `getCorruptECBlockGroups` expose counters.

## Control flow

Adding a corrupt replica creates the per-block datanode map if absent and increments replicated or EC block-group counters once per block key. Duplicate adds update the reason and log as duplicate. Removing a datanode entry optionally checks that the stored reason matches, deletes the per-block map when empty, and decrements the corresponding counter. Testing ID pagination filters block type through `BlockIdManager`, starts from the requested ID or beginning, sorts, limits to 100, and returns IDs.

## State and persistence behavior

The class is an in-memory map from `Block` to datanode-to-reason maps plus counters. Corruption knowledge is reconstructed or persisted by higher-level NameNode metadata mechanisms, not by this class directly.

## Dependencies and integration points

It integrates with `BlockManager`, block reports, client/datanode corruption reports, `NameNode.blockStateChangeLog`, IPC remote IP logging, `BlockIdManager`, and replicated versus striped block accounting.

## Risks and edge cases

The map is not internally synchronized and relies on NameNode locking. The key type is `Block`, so equality/generation-stamp semantics matter. Counters depend on correct `isStriped` values passed on add/remove. Reason-specific removal ignores mismatches and can leave stale corruption if reason classification changes.

## Test signals

Tests should cover add/update duplicates, per-node and whole-block removal, reason-specific removal, counter increments/decrements for replicated and striped blocks, corrupt ID pagination bounds, and get-reason behavior for missing entries.
