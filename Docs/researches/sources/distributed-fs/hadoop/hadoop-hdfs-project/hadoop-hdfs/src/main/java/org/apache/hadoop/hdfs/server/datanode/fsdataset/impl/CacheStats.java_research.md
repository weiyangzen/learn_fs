# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/CacheStats.java

Purpose: tracks approximate memory-cache usage and capacity for DataNode block caching, using OS page-size rounding.

Important APIs/types/functions: `PageRounder` obtains OS page size from `NativeIO.POSIX.getCacheManipulator()` and provides `roundUp`/`roundDown`. Inner `UsedBytesCount` stores an `AtomicLong` and implements CAS-based `reserve`, `release`, `releaseRoundDown`, and `get`. Public/package methods expose `getCacheUsed`, `getCacheCapacity`, `reserve`, `release`, `releaseRoundDown`, `getPageSize`, and `roundUpPageSize`.

Control flow: cache loaders call `reserve` before mapping/locking a block. The count is rounded up and rejected with `-1` if it would exceed capacity. Failed or completed cache operations call release methods. `releaseRoundDown` is used for locked-memory accounting where OS page multiples matter.

State and persistence: all state is in-memory. `usedBytes` intentionally overestimates by counting pending cache operations and not pending uncaches; this conservative view helps avoid NameNode over-assignment.

Dependencies and integration points: used by `FsDatasetCache` and cache loader implementations. Depends on `NativeIO` for page size and `AtomicLong` for concurrency.

Risks: release methods can drive the counter negative if call pairs are wrong. Rounding assumes page size is a power of two because it uses bit masking. Capacity is fixed after construction. The estimate is approximate by design and may differ from actual locked memory.

Test signals: reserve success/failure at capacity, page rounding, CAS behavior under concurrency, release and releaseRoundDown accounting, and negative-count detection in higher-level tests.
