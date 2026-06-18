# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlockLoaderFactory.java

`MappableBlockLoaderFactory` selects the DataNode cache loader implementation. It is a non-instantiable final class with one public static API, `createCacheLoader(DNConf conf)`.

The decision tree is: no configured pmem volumes returns `MemoryMappableBlockLoader`; pmem plus native IO and PMDK availability returns `NativePmemMappableBlockLoader`; pmem without PMDK returns `PmemMappableBlockLoader`.

The factory holds no state and persists nothing. Its choice determines whether cache behavior is transient DRAM, native pmem, or file-backed pmem. It depends on `DNConf.getPmemVolumes()` and `NativeIO.POSIX.isPmdkAvailable()`, and is consumed by `FsDatasetCache`.

Risks include native availability misdetection and surprising fallback to non-native pmem when PMDK is unavailable. Tests should cover all three branches and verify resulting loader transient/native flags after initialization.
