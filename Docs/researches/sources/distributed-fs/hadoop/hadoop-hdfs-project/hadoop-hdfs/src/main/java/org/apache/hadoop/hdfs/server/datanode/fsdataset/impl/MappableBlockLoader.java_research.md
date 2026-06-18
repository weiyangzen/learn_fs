# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoader.java

`MappableBlockLoader` is the abstract base for DataNode cache loaders. It defines initialization, block loading, cache reservation/release, usage/capacity reporting, transient/native flags, persistent-memory recovery, and shutdown hooks.

Abstract APIs include `initialize`, `load`, `reserve`, `release`, `getCacheUsed`, `getCacheCapacity`, `isTransientCache`, `isNativeLoader`, and `getRecoveredMappableBlock`. The default `shutdown` does nothing. Protected helpers `verifyChecksum` and `fillBuffer` implement shared checksum verification over block and metadata file channels.

Concrete `load` implementations map or copy the block, then call `verifyChecksum`. Verification reads the metadata header, obtains `DataChecksum`, allocates up to 8 MiB of block data per batch plus matching checksum bytes, fills both buffers, and calls `verifyChunkedSums`. Premature EOF, missing channels, or checksum mismatch raises `IOException`.

The base class holds no fields and persists nothing; reservation state belongs to concrete loaders such as DRAM `CacheStats` or pmem allocators. It integrates with `FsDatasetCache`, `MemoryMappableBlockLoader`, pmem loaders, `DNConf`, `ExtendedBlockId`, `BlockMetadataHeader`, and `DataChecksum`.

Risks include expensive checksum I/O, stream-position assumptions, cleanup on verification failure, and edge cases around partial final chunks. Tests should cover checksum success/failure, premature EOF, missing channels, final partial chunks, reservation failure propagation, pmem recovery, and shutdown cleanup.
