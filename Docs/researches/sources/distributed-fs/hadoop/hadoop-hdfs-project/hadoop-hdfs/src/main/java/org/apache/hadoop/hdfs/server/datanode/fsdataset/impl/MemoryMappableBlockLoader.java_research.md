# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappableBlockLoader.java

`MemoryMappableBlockLoader` is the transient DRAM cache loader. It memory-maps a block file, locks the pages into memory, verifies the block checksum, and returns a `MemoryMappedBlock`.

It owns `CacheStats memCacheStats`. `initialize` creates `CacheStats` from `DNConf.getMaxLockedMemory`. `load` obtains the block file channel, maps it read-only, calls `NativeIO.POSIX.getCacheManipulator().mlock`, verifies checksums through `MappableBlockLoader.verifyChecksum`, and constructs `MemoryMappedBlock`. If construction fails, the finally block unmaps the buffer to release locked memory. `reserve`, `release`, `getCacheUsed`, and `getCacheCapacity` delegate to `CacheStats`; `isTransientCache` returns true, `isNativeLoader` false, and recovery returns null.

State is runtime-only: locked mmap pages plus cache accounting. There is no persistent recovery. It is selected when no pmem volumes are configured and integrates with `FsDatasetCache`, native IO, file channels, and `MemoryMappedBlock`.

Risks include native `mlock`/`munmap` platform behavior, invalid map lengths, missing file channels, and cleanup on checksum failure. Tests should cover capacity initialization, successful mmap/mlock/checksum, failure cleanup, reserve/release accounting, null recovery, flags, and close-driven unmapping.
