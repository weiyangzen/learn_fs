# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappableBlockLoader.java

## Purpose

`NativePmemMappableBlockLoader` is the PMDK-backed persistent-memory cache loader for DataNode block caching. It maps a selected PMem cache file through `NativeIO.POSIX.Pmem`, verifies block checksums while copying block bytes into the mapped region, and returns a `NativePmemMappedBlock` that exposes the native address to the cache subsystem.

## Important APIs, Control Flow, and State

The important methods are `initialize(DNConf)`, `load(...)`, `verifyChecksumAndMapBlock(...)`, `isNativeLoader()`, and `getRecoveredMappableBlock(...)`. `load` obtains the source block `FileChannel`, asks `PmemVolumeManager` for the reserved cache path, maps it with `POSIX.Pmem.mapBlock(path, length, false)`, streams block/meta chunks through `DataChecksum.verifyChunkedSums`, copies verified bytes with `POSIX.Pmem.memCopy`, syncs the region with `memSync`, and creates the mapped-block handle. Recovery remaps an existing cache file with `mapBlock(..., true)`, reconstructs the `ExtendedBlockId` from the filename and block pool id, and restores the key-to-volume mapping in `PmemVolumeManager`.

State is mostly external: the cache file, native mapped address/length, and `PmemVolumeManager`'s block-to-volume index. On failure before a `NativePmemMappedBlock` is created, the loader unmaps the region and deletes the mapped file. Checksum and copy processing uses 8 MiB chunk groups sized by the block's checksum layout, so partial EOF and checksum failures abort before exposing the block as cached.

## Dependencies, Integration, Risks, and Tests

This class depends on `PmemMappableBlockLoader`, `PmemVolumeManager`, `BlockMetadataHeader`, `DataChecksum`, `NativeIO.POSIX.Pmem`, `FsDatasetUtil`, and `ExtendedBlockId`. It integrates with `FsDatasetCache` through the `MappableBlockLoader` abstraction and with PMem recovery through `getRecoveredMappableBlock`.

Risks include native-library availability, null cache paths if reservation state is missing, incorrect unmap/delete cleanup on partial copy, and native length/page alignment behavior. Tests should cover successful cache load, checksum failure cleanup, premature EOF, recovery of existing cache files, unavailable native PMem, and no stale mapped files left after failure.
