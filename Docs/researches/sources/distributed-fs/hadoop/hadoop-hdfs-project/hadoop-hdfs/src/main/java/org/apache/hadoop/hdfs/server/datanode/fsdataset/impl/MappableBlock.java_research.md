# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/MappableBlock.java

`MappableBlock` is the cache-layer abstraction for an HDFS block mapped into a DataNode cache region. It extends `Closeable` and exposes `getLength()`, `getAddress()`, and `getKey()`.

Implementations report cached byte length, optionally expose a native cache address, and optionally expose an `ExtendedBlockId`. The address contract uses `-1` when no direct address is available; some implementations may also return null keys.

The interface has no control flow or persistence itself. Implementations may own mmap buffers, native persistent-memory addresses, cache files, or block identifiers. `close()` is the lifecycle boundary for unmapping or releasing native resources.

It is consumed by `MappableBlockLoader` implementations and `FsDatasetCache`. Main risks are assuming address/key support across implementations and failing to close mapped resources. Tests should verify implementation-specific length, address/key semantics, idempotent close behavior, and cache release integration.
