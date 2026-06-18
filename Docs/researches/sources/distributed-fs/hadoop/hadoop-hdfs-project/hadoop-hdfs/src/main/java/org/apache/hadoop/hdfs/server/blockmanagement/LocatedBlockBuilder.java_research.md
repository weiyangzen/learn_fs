<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java

## Purpose

`LocatedBlockBuilder` is a small NameNode-side builder for `LocatedBlocks` responses. It accumulates file length, under-construction state, located block entries, the last block, encryption metadata, and erasure-coding policy before producing the protocol object returned to HDFS clients.

## Important APIs and types

The builder exposes fluent package-private setters `fileLength`, `addBlock`, `lastUC`, `lastBlock`, `lastComplete`, `encryption`, and `erasureCoding`. `isBlockMax` enforces a caller-provided maximum block count. `newLocatedBlock` delegates to `BlockManager.newLocatedBlock` so callers can still set block tokens on the returned object. `build(DatanodeDescriptor)` exists as an overridable hook and normally delegates to `build()`.

## Control flow

Callers create the builder with a max block limit, add `LocatedBlock` instances as block metadata is scanned, optionally attach last-block and security metadata, then call `build`. The internal block list starts as `Collections.emptyList()` and switches to an `ArrayList` on the first `addBlock`.

## State and persistence behavior

All state is transient request state. There is no persistence, synchronization, or defensive copying beyond constructing the final `LocatedBlocks` object with the accumulated list reference.

## Dependencies and integration points

It integrates `BlockManager`, `DatanodeStorageInfo`, `DatanodeDescriptor`, `LocatedBlock`, `LocatedBlocks`, `ExtendedBlock`, `FileEncryptionInfo`, and `ErasureCodingPolicy`. `ProvidedStorageMap.ProvidedBlocksBuilder` subclasses it to rewrite provided-storage locations.

## Risks and edge cases

The builder is mutable and package-private; it assumes single-threaded request construction. The `maxBlocks` limit is advisory because `addBlock` itself does not reject overflow. Subclasses must preserve `LocatedBlocks` semantics when overriding location construction or client-aware build hooks.

## Test signals

Useful signals include max-block boundary behavior, empty file construction, last-block and under-construction combinations, encryption/EC metadata propagation, and subclass behavior for provided storage location expansion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/blockmanagement/LocatedBlockBuilder.java -->
