# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MemoryMappedBlock.java

`MemoryMappedBlock` is the DRAM mmap-backed implementation of `MappableBlock`. It stores a `MappedByteBuffer` and immutable cached length.

`getLength` returns the cached byte count. `getAddress` returns `-1L` because this Java mmap implementation does not expose a native address. `getKey` returns null because the implementation does not store an `ExtendedBlockId`. `close` calls `NativeIO.POSIX.munmap` when the buffer is non-null and then nulls it, making repeated close calls harmless at this level.

The mapped state is transient virtual memory backed by the original block file; no cache file or identity is persisted. It is created by `MemoryMappableBlockLoader` and managed by `FsDatasetCache`.

Risks are consumers assuming address/key are available, concurrent use after close, and native unmap platform behavior. Tests should verify length, sentinel address/key values, idempotent close, and cache eviction/release integration.
