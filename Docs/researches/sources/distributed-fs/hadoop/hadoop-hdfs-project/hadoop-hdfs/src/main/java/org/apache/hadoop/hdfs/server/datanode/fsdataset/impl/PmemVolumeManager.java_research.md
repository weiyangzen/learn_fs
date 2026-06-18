# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemVolumeManager.java

## Purpose

`PmemVolumeManager` is the singleton allocator, path resolver, recovery scanner, and cleanup owner for DataNode persistent-memory cache volumes. It validates configured PMem directories, tracks per-volume capacity/usage, maps each cached `ExtendedBlockId` to a volume index, and constructs hierarchical cache paths.

## Important APIs, Control Flow, and State

Important APIs include `init`, `getInstance`, `reserve`, `release`, `loadVolumes`, `recoverCache`, `recoverBlockKeyToVolume`, `verifyIfValidPmemVolume`, `createBlockPoolDir`, `chooseVolume`, `idToCacheFilePath`, and `getCachePath`. Initialization requires at least one configured PMem directory, creates/uses an `hdfs_pmem_cache` child directory, optionally cleans it if recovery is disabled, verifies mmap/write/force/delete behavior with a temporary file, and initializes `UsedBytesCount` counters using usable space or test override.

Reservations are synchronized and use round-robin `chooseVolume` with capacity checks; successful reservations insert `blockKeyToVolume`. Release removes that mapping and decrements the selected counter. Recovery walks each volume's block-pool directory recursively, asks the active cache loader to rebuild a `MappableBlock`, updates key-to-volume mappings, increases capacity by recovered bytes, and reserves the recovered used bytes. Cache paths are `pmemVolume/bpid/subdirN/subdirM/blockId`, with subdirectory numbers derived from block-id bits.

## Dependencies, Integration, Risks, and Tests

The manager depends on Commons IO directory traversal/cleanup, `NativeIO.POSIX.munmap`, `MappedByteBuffer`, `FsDatasetUtil`, `ExtendedBlockId`, and HDFS PMem configuration keys. It is shared by both native and non-native PMem loaders and mapped-block cleanup classes.

Risks include singleton lifecycle issues in tests, non-atomic interaction between reservation and file creation, `release` assuming a present mapping, recursive recovery accepting unexpected files, max-capacity adjustment during recovery, and cleanup deleting all files under configured PMem cache directories. Tests should cover invalid volume filtering, capacity exhaustion, round-robin selection, path layout, block-pool directory creation, recovery accounting, cleanup behavior, and concurrent reserve/release.
