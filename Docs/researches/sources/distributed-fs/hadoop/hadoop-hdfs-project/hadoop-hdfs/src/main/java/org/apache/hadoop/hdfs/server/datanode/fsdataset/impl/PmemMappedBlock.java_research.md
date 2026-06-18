# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/PmemMappedBlock.java

## Purpose

`PmemMappedBlock` represents a DataNode block cached on a PMem filesystem without a native mapped address. It is the lightweight handle returned by `PmemMappableBlockLoader`.

## Important APIs, Control Flow, and State

The implementation stores only `length` and `ExtendedBlockId`. `getLength()` and `getKey()` expose that metadata; `getAddress()` returns `-1L` to signal that no native address is available. `close()` resolves the cache path through `PmemVolumeManager`, deletes the cache file, and logs success or warning.

State is in-memory for the handle and persistent on disk for the cache file until close or loader shutdown. There is no explicit volume accounting update in this class; release accounting is handled by the cache manager and `PmemMappableBlockLoader`.

## Dependencies, Integration, Risks, and Tests

The class depends on `MappableBlock`, `PmemVolumeManager`, `FsDatasetUtil`, and `ExtendedBlockId`. It integrates with non-native PMem cache reads where the cache file path, rather than an address, is the durable identity.

Risks include silent cleanup failure and a null path if the volume-manager mapping was already removed. Tests should verify address sentinel behavior, close deletes the expected file, repeated close behavior is acceptable, and warning paths do not break cache-manager cleanup.
