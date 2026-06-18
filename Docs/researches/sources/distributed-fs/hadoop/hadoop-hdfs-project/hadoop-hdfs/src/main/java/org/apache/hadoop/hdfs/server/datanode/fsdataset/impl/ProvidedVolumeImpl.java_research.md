# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/ProvidedVolumeImpl.java

## Purpose

`ProvidedVolumeImpl` implements an `FsVolumeImpl` for HDFS PROVIDED storage: blocks are not physically stored by the DataNode, but described by an external `BlockAliasMap<FileRegion>` and served from a remote `FileSystem`. The class presents those external regions as finalized replicas while rejecting write-oriented volume operations.

## Important APIs, Control Flow, and State

Key nested types are `ProvidedVolumeDF`, `ProvidedBlockPoolSlice`, `ProvidedBlockIteratorState`, and `ProviderBlockIteratorImpl`. The constructor enforces `StorageType.PROVIDED`, records the base URI, and opens the remote filesystem. `addBlockPool` creates a slice with a configurable alias-map implementation, defaulting to `TextFileRegionAliasMap`. `getVolumeMap` calls each slice's `fetchVolumeMap`, which retries alias-map reader creation, filters `FileRegion` entries whose paths belong under the volume URI, builds finalized `ReplicaInfo` objects with path prefix/suffix, offset, length, generation stamp, optional `PathHandle` from nonce bytes, and remote FS, then inserts them into the global `ReplicaMap` unless a local replica already exists.

Provided volume state is mostly in memory: `bpSlices`, per-slice `ReplicaMap`, block counts, and synthetic DFS-used counters. The durable source of truth is the alias map and remote storage. Directory scan/report flow calls `aliasMap.refresh()` and emits `ScanInfo` for current regions. Block iterators do not persist local cursor state; `save` only updates timestamps and `load` rewinds. Capacity is reported as DFS used, available is clamped to zero, non-DFS used is zero, and write/reservation/temp/RBW/lazy-persist operations throw `UnsupportedOperationException`.

## Dependencies, Integration, Risks, and Tests

This class integrates with provided-storage alias maps, `ReplicaBuilder`, `ReplicaMap`, `DirectoryScanner.ReportCompiler`, `FsDatasetImpl`, `FileSystem`, `PathHandle`, and `VolumeCheckResult`. It also inherits common volume behavior from `FsVolumeImpl` while overriding most mutation paths as unsupported.

Risks include alias-map reader failure silently producing an empty provided volume, URI prefix filtering mistakes in `containsBlock`, assumptions that alias-map iteration is sorted for iterator resume semantics, duplicate block IDs being skipped if local replicas exist, and stale in-memory volume maps after alias-map changes. Tests should cover suffix extraction, local and absolute URI containment, alias-map retry behavior, replica construction with nonce/path handle, duplicate handling, directory scan refresh, block iterator rewind/load, and that all unsupported write paths fail predictably.
