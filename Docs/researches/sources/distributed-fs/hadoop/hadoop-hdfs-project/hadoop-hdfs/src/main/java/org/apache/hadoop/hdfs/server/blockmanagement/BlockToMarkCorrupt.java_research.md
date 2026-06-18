# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/BlockToMarkCorrupt.java

## Purpose

`BlockToMarkCorrupt` is a small value object used while processing block reports to collect replicas that should be marked corrupt. It preserves both the datanode-reported corrupted block and the NameNode-stored block metadata.

## Important APIs and types

- Constructors require corrupted `Block`, stored `BlockInfo`, textual reason, and `CorruptReplicasMap.Reason`.
- The generation-stamp constructor mutates the corrupted block to a supplied generation stamp.
- `isCorruptedDuringWrite` compares stored and corrupted generation stamps.
- Accessors expose corrupted block, stored block, reason text, and reason code.
- `toString` shows whether corrupted and stored references are the same object.

## Control flow

Construction validates non-null block references. For generation-stamp mismatch scenarios, the second constructor delegates and then adjusts the corrupted block's generation stamp to represent the exact reported mismatch. Later block-report code can decide whether corruption happened during write and record the reason in `CorruptReplicasMap`.

## State and persistence behavior

The class is in-memory and short-lived. It mutates the supplied corrupted `Block` in one constructor, but persistent corruption state is stored later in `CorruptReplicasMap`.

## Dependencies and integration points

It is tied to block-report reconciliation, `BlockManager`, `BlockInfo`, `Block`, and corruption reason codes.

## Risks and edge cases

Mutating the corrupted block's generation stamp can surprise callers if the same `Block` instance is shared. `isCorruptedDuringWrite` only checks generation-stamp ordering and does not account for length or replica state mismatches.

## Test signals

Tests should cover null validation, generation-stamp mutation, corruption-during-write classification, reason propagation, and string output for same versus different stored block references.
