<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java

## Purpose

`FileRegion` represents a provided-storage block alias backed by a byte range in an external file path.

## Important APIs and types

It implements `BlockAlias` and stores a `Pair<Block, ProvidedStorageLocation>`. Constructors accept block ID, `Path`, offset, length, optional generation stamp, optional nonce, or direct `Block` plus `ProvidedStorageLocation`. APIs expose `getBlock`, `getProvidedStorageLocation`, equality, and hash code.

## Control flow

Construction creates a `Block` with the supplied length/generation stamp and a `ProvidedStorageLocation` with path, offset, length, and nonce. Alias-map readers then return `FileRegion` objects to provided-storage block report processing.

## State and persistence behavior

Instances are immutable after construction. Persistence depends on the alias-map implementation that serializes/deserializes file regions, such as text or LevelDB maps.

## Dependencies and integration points

It integrates with `BlockAliasMap`, `ProvidedStorageMap`, `Block`, `Path`, `ProvidedStorageLocation`, and the grandfather generation-stamp constant for older constructors.

## Risks and edge cases

No validation is performed on offset, length, nonce, or path. Equality includes both block and location, so two aliases for the same block but different external range are different `FileRegion` values.

## Test signals

Tests should cover constructor variants, default generation stamp, nonce preservation, equality/hash behavior, and alias-map round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/common/FileRegion.java -->
