# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappableBlockLoader.java

## Purpose

`PmemMappableBlockLoader` is the default file-backed persistent-memory cache loader that does not use PMDK native mappings. It copies a block into a PMem-backed filesystem path managed by `PmemVolumeManager`, verifies checksums against the copied data, and returns a `PmemMappedBlock` cache handle.

## Important APIs, Control Flow, and State

`initialize(DNConf)` initializes the singleton `PmemVolumeManager`, records whether cache recovery is enabled, and returns `CacheStats(0)` because PMem is used instead of locked DRAM. `load(...)` gets the block channel, resolves the reserved cache path, writes block bytes into a `RandomAccessFile` via `transferTo`, rewinds the cache file channel, verifies the cached bytes with inherited `verifyChecksum`, and returns a `PmemMappedBlock`. `reserve`, `release`, `getCacheUsed`, and `getCacheCapacity` are delegated to the volume manager.

The PMem file is persistent state. If loading fails, the partially copied mapped file is deleted. `getRecoveredMappableBlock` reconstructs the `ExtendedBlockId` from the cache filename and block pool id, creates a `PmemMappedBlock` using the cache file length, and restores the manager's volume mapping. `shutdown` deletes PMem cache contents only when recovery is disabled.

## Dependencies, Integration, Risks, and Tests

This loader depends on `MappableBlockLoader`, `PmemVolumeManager`, `PmemMappedBlock`, `DNConf`, `IOUtils`, and `FsDatasetUtil`. It is selected by cache-loader factory logic for PMem caching and integrates with the broader cache accounting path through `reserve/release`.

Risks include mismatches between reservation state and cache path lookup, partial `transferTo` behavior on some filesystems, checksum verification only after copy, and stale persistent cache files if recovery settings are wrong. Tests should cover reservation/release accounting, failed checksum cleanup, recovery-enabled shutdown preserving files, recovery-disabled shutdown cleanup, and block-id parsing from cache filenames.
