# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/NativePmemMappedBlock.java

## Purpose

`NativePmemMappedBlock` is the `MappableBlock` implementation for a block cached in persistent memory through a native PMDK mapping. It holds the mapped address, mapped length, and `ExtendedBlockId` needed by the cache and cleanup paths.

## Important APIs, Control Flow, and State

The public interface comes from `MappableBlock`: `getLength()`, `getAddress()`, `getKey()`, and `close()`. Construction asserts a positive length and stores the native address. `close` is idempotent through the `pmemMappedAddress != -1L` guard: it resolves the cache path through `PmemVolumeManager`, calls `NativeIO.POSIX.Pmem.unmapBlock`, marks the address invalid, deletes the cache file, and logs the uncache event.

State is per cached replica and in-memory only, while the cache file itself is durable until `close` deletes it. Exceptions during close are logged as warnings rather than propagated, which is consistent with cache cleanup paths but can leave files or mappings behind if native unmap fails.

## Dependencies, Integration, Risks, and Tests

The class integrates with `NativePmemMappableBlockLoader`, `PmemVolumeManager`, `NativeIO.POSIX.Pmem`, and `FsDatasetUtil`. `getAddress()` distinguishes this implementation from non-native `PmemMappedBlock`, which returns `-1`.

Risks center on cleanup reliability: cache path lookup can fail, native unmap may report false, and delete failure is swallowed after logging. Tests should assert idempotent close, native unmap invocation, cache-file deletion, warning behavior on failures, and that recovered native mappings use the expected key and length.
