# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/datanode/fsdataset/impl/FsDatasetCache.java

Purpose: manages DataNode block caching by mapping and locking blocks into DRAM or persistent memory, verifying checksums before advertisement, and handling uncache requests safely around short-circuit readers.

Important APIs/types/functions: `Value` pairs `MappableBlock` with `State`; states are `CACHING`, `CACHING_CANCELLED`, `CACHED`, and `UNCACHING`, with only `CACHED` advertised. Constructor creates uncache executors, validates revocation polling config, creates a `MappableBlockLoader`, and initializes `CacheStats`. `initCache` creates persistent-memory block-pool dirs and optionally recovers cached blocks. `cacheBlock` inserts `CACHING` and schedules `CachingTask`; `uncacheBlock` transitions to cancelled or uncaching and schedules immediate/deferred `UncachingTask`. Metrics and query methods expose cache usage, capacity, failure counts, cached block IDs, PMEM paths/addresses, and `isCached`.

Control flow: caching reserves cache bytes, opens block and metadata streams from the dataset, asks the loader to checksum/map/lock, then atomically publishes `CACHED` unless cancelled. Failure closes streams, releases reservation, closes any mapped block, increments failure metrics, and removes the map entry. Uncaching may defer while DRAM short-circuit clients keep anchors; after timeout it forcibly uncaches, closes the mappable block, removes map state, releases bytes, and increments metrics.

State and persistence: `mappableBlockMap` and counters are synchronized/in-memory. DRAM cache is transient. Persistent-memory mode can recover cache state across restart and stores cache files under PMEM-managed paths.

Dependencies and integration points: depends on `FsDatasetImpl`, `DNConf`, `MappableBlockLoaderFactory`, `PmemVolumeManager`, `DatanodeUtil`, `ExtendedBlockId`, short-circuit registry, DataNode metrics, `CacheStats`, and checksum exceptions.

Risks: state transitions must remain synchronized; async tasks use map state as authority. Reservation release must match loader behavior. Deferred uncache can hold memory while clients retain anchors, then forcibly revoke after timeout. Persistent cache recovery must align with real block validity. `getCacheAddress` reads map state without explicit synchronization after `isCached`.

Test signals: duplicate cache request failure, successful cache advertisement only after checksum/load, cancellation during caching, cache reservation failure, file-not-found and checksum failures, immediate and deferred uncache, revocation timeout, PMEM recovery/path/address, metrics increments, and shutdown loader cleanup.
