# Research: subset-b-007999

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/KeyValueStreamDataChannel.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/KeyValueStreamDataChannel.java

Purpose: Implements the Ratis `StateMachine.DataChannel` used by key-value containers for streaming writes, buffering incoming `ByteBuffer` data and writing only the chunk payload to the block file.

Important APIs and functions: `write()` records StreamWrite metrics, checks closed state and container space, and delegates to `writeBuffers()`. `writeBuffers(ReferenceCountedObject, Buffers, WriteMethod)` drains whole buffers and releases references. `writeFully()` loops until the file channel accepts all bytes. `close()` flushes buffered content before closing. `setEndIndex()` and `readProtoLength()` strip the trailing PutBlock proto from the stream frame.

Control flow and state: The instance owns a `Buffers` accumulator and an atomic `closed` flag. Normal writes feed the accumulator; close polls all remaining bytes, moves the Netty writer index to the start of the trailing proto, writes payload bytes, releases the retained buffer, then closes the base channel. `cleanupInternal()` drops all buffered data and closes if the stream was never linked.

Persistence and dependencies: File persistence is inherited from `StreamDataChannelBase` over `RandomAccessFile`/`FileChannel`. It integrates with Ratis reference-counted buffers, Netty `ByteBuf`, `RatisHelper` debug logging, `ContainerMetrics`, and `ContainerData` space accounting.

Risks: Reference counting must remain balanced across offered buffers and the final `pollAll()` retain/release pair. `setEndIndex()` assumes the last four bytes encode proto length; corrupt or partial frames can set an invalid writer index. Returning `src.get().remaining()` after offers means callers depend on buffer mutation semantics. A non-positive file-channel write is treated as fatal.

Test signals: Cover stream writes split across frame boundaries, close with trailing PutBlock proto, malformed proto lengths, writes after close, cleanup of unlinked channels, reference release under exceptions, and metrics/space accounting for payload bytes only.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/KeyValueStreamDataChannel.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/MappedBufferManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/MappedBufferManager.java

Purpose: Manages a process-wide cache of memory-mapped read buffers while bounding the number of active mappings through a semaphore quota.

Important APIs and functions: The constructor sets quota capacity and a striped lock table. `getQuota()` attempts to acquire permits and launches asynchronous cleanup of cleared weak references when quota is exhausted. `releaseQuota()` returns permits. `availableQuota()` exposes current permits. `computeIfAbsent()` locks by file/position/size key, returns a live cached buffer or installs a newly supplied buffer.

Control flow and state: `mappedBuffers` is static and maps string keys to weak references, so mappings can be reused across manager instances but reclaimed by GC. `cleanupInProgress` prevents concurrent cleanup passes. `Striped.lazyWeakLock(1024)` serializes one cache key without global locking.

Persistence and dependencies: No direct persistence occurs, but cached `ByteBuffer` instances typically wrap memory-mapped file regions used by chunk reads. It depends on Guava `Striped`, Java weak references, `ConcurrentHashMap`, `Semaphore`, and `CompletableFuture`.

Risks: Quota is optimistic: callers must acquire before compute, and a cache hit releases one permit because no new mapping was consumed. Incorrect caller ordering can leak or over-release permits. Static cache state crosses container/file lifetimes. Async cleanup is best-effort and does not force unmapping. Key construction by string concatenation must remain collision-free for file names, positions, and sizes.

Test signals: Exercise quota acquisition/failure, cached hit permit release, weak-reference cleanup permit restoration, concurrent `computeIfAbsent()` for the same key, concurrent different-key access, null supplier result, and manager reuse across files.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/MappedBufferManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/StreamDataChannelBase.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/StreamDataChannelBase.java

Purpose: Provides the common file-backed `StateMachine.DataChannel` implementation for stream write channels, including file open/close, force, space checks, metrics, and cleanup lifecycle.

Important APIs and functions: The constructor opens the target block file as `RandomAccessFile("rw")`. `force()` syncs the file channel. `isOpen()` reports channel state. `assertSpaceAvailability()` validates requested bytes against the container volume. `setLinked()` marks the channel as attached to a committed block. `cleanUp()` invokes subclass cleanup if not linked. `writeFileChannel()` writes bytes and updates metrics and container stats.

Control flow and state: The base class tracks `linked` and `cleaned` atomically to avoid deleting or closing a channel that was successfully linked into the container. Subclasses supply the operation type and cleanup body. I/O exceptions call `checkVolume()`, which reports the volume through `StorageVolumeUtil.onFailure()`.

Persistence and dependencies: This class writes to the local block file and updates `ContainerData.updateWriteStats()` plus `ContainerMetrics` byte and latency counters. It depends on Ratis `StateMachine.DataChannel`, Ozone `ContainerData`, volume failure utilities, and Hadoop monotonic time.

Risks: Cleanup semantics depend on `setLinked()` being called by higher-level code at the right time. Space checks are performed before writes but cannot prevent concurrent exhaustion. Metrics update after each low-level write uses the actual byte count; zero or negative writes are handled by subclass loops. Failure handling marks the whole volume suspect on I/O errors.

Test signals: Cover constructor failure for missing files, `force()` error paths, linked versus unlinked cleanup, repeated cleanup calls, write metrics/stat updates, volume failure signaling on exceptions, and close idempotency through subclasses.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/StreamDataChannelBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/package-info.java

Purpose: Documents the `org.apache.hadoop.ozone.container.keyvalue.impl` package as the implementation layer for key-value container block and chunk managers.

Important APIs and functions: The file contains only package documentation and the package declaration. It scopes implementation classes such as stream data channels, chunk strategies, block managers, and cache helpers under the key-value container type.

Control flow and state: No runtime control flow or state is declared here. The package boundary separates concrete container behavior from the public `keyvalue.interfaces` contracts and from common container abstractions.

Persistence and dependencies: Persistence behavior is supplied by classes in the package, especially block/chunk file writes and RocksDB metadata updates. This file has no imports or direct dependencies.

Risks: Documentation-only files can drift from package responsibilities as implementation classes are added. Keeping this package focused matters because dispatchers and handlers depend on the distinction between interfaces and implementations.

Test signals: Compile/package checks and documentation review are sufficient; behavioral tests belong to the concrete implementation classes in this package.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/BlockManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/BlockManager.java

Purpose: Defines the block-level contract for key-value containers: create/update, read, delete, list, existence, committed length, finalization, read tuning, and shutdown.

Important APIs and functions: `putBlock()` has normal and end-of-block variants. `putBlockForClosedContainer()` persists block data for closed replicas with optional BCSID overwrite. `getBlock()`, `deleteBlock()`, `listBlock()`, `blockExists()`, and `getCommittedBlockLength()` expose block metadata operations. `finalizeBlock()` records finalized blocks. Read configuration getters expose default buffer size, mapped-buffer thresholds, mapped-buffer count, and Netty chunked read mode.

Control flow and state: This is an interface; state is held by implementations and their backing `DatanodeStore`. The API separates block metadata from chunk data while documenting that closed-container import/update expects the caller to update used bytes through chunk writes.

Persistence and dependencies: Integrates `Container`, `BlockData`, `BlockID`, `ChunkInfo`, and `DispatcherContext`. Implementations persist to container RocksDB tables and coordinate with `ChunkManager` for data-file side effects.

Risks: Inconsistent BCSID checks or overwrite behavior can expose stale blocks. `putBlockForClosedContainer()` requires caller-side used-byte accounting, which is easy to miss. Finalized-block state must stay synchronized with container schema support. Read tuning values influence memory mapping and Netty paths.

Test signals: Cover all put/get/delete/list paths, closed-container overwrite and BCSID mismatch behavior, committed length for absent and present blocks, finalization persistence, read-buffer configuration propagation, and shutdown under active operations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/BlockManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/ChunkManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/ChunkManager.java

Purpose: Defines the chunk-level data contract for key-value containers, covering chunk write/read/delete, bulk delete, streaming setup, write finalization hooks, and read-buffer sizing.

Important APIs and functions: `writeChunk()` accepts `ChunkBuffer` and has a default `ByteBuffer` wrapper. `readChunk()` returns `ChunkBufferToByteString`. `deleteChunk()` and `deleteChunks()` remove chunk files. `finishWriteChunks()`, `finalizeWriteChunk()`, `streamInit()`, and `getStreamDataChannel()` are optional hooks for layouts that support streaming. `getBufferCapacityForChunkRead()` computes read buffer capacity from chunk flags and checksum data.

Control flow and state: The interface is stateless, with no-op defaults for optional lifecycle hooks. Buffer sizing prefers single-buffer reads for old clients, checksum-boundary buffers for checksummed reads, configured defaults for checksum type NONE, and chunk length as fallback.

Persistence and dependencies: Implementations touch container chunk files and may update metadata through `BlockData`. It integrates with `Container`, `KeyValueContainer`, `BlockID`, `ChunkInfo`, `ContainerMetrics`, `DispatcherContext`, Ratis `StateMachine.DataChannel`, checksum metadata, and Ozone buffer wrappers.

Risks: Partial read/write support is explicitly incomplete. Buffer capacity can overflow `int`, and the helper throws on overflow. Optional stream methods returning null require callers to guard by implementation capability. Chunk deletion must remain consistent with block metadata deletion.

Test signals: Cover write/read/delete for file-per-block and file-per-chunk layouts, ByteBuffer wrapper behavior, checksum NONE and non-NONE buffer sizing, old-client single-buffer reads, integer overflow, streaming init/data-channel support, and no-op default finalization paths.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/ChunkManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/package-info.java

Purpose: Documents the interface package for key-value container block and chunk manager contracts.

Important APIs and functions: The package contains contracts such as `BlockManager` and `ChunkManager`, which are consumed by handlers, dispatchers, and container operations while implemented by layout-specific classes.

Control flow and state: No runtime logic appears in this file. It marks a boundary where container operations depend on abstract APIs instead of concrete storage layouts.

Persistence and dependencies: Persistence is indirect through implementations that write chunk files and RocksDB metadata. This file has no imports or direct runtime dependency.

Risks: If new contracts are added outside this package, handler code may become more tightly coupled to implementation classes. Documentation should continue to reflect the public surface of key-value container managers.

Test signals: Build and package-level documentation checks; behavioral testing belongs to the interfaces' implementors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/interfaces/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java

Purpose: Documents the root package for the KeyValue container type.

Important APIs and functions: The package groups core key-value container classes, data objects, helpers, packers, and subpackages for manager interfaces, implementations, and background state-machine tasks.

Control flow and state: No executable code or state is present. The file clarifies the package boundary around one container type used by the datanode container subsystem.

Persistence and dependencies: Persistence is provided by classes under this package and `container.metadata`; this documentation file has no direct dependencies.

Risks: Package-level documentation can become too broad as features such as reconciliation, streaming, or schema migration grow. Keeping a clear package boundary helps prevent cross-container-type coupling.

Test signals: Compile and javadoc/package checks; runtime test signals are in concrete KeyValue container classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/BlockDeletingTask.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/BlockDeletingTask.java

Purpose: Implements the background task that physically deletes blocks/chunks for key-value containers and reconciles delete metadata, statistics, checksums, and pending-delete counters across datanode DB schemas.

Important APIs and functions: `call()` repeatedly invokes `handleDeleteTask()` until the assigned block budget is consumed or no progress is made. `deleteViaSchema1()` scans deleting block keys in the block table. `deleteViaSchema2()` and `deleteViaSchema3()` read delete transaction tables and delegate to `deleteViaTransactionStore()`. `deleteTransactions()` performs chunk deletion through the container `Handler`, handles duplicate local IDs, and tracks released/processed bytes.

Control flow and state: The task locks the live container through `ContainerSet.getContainerWithWriteLock()`, refreshes `containerData` from the locked container, opens the DB, branches by schema, deletes files first, records deleted blocks in the checksum tree, then batches DB metadata removal and counter updates. Schema v3 uses container-prefixed transaction keys; schema v2 uses long transaction IDs.

Persistence and dependencies: It persists changes to block tables, last-chunk tables, delete transaction tables, DB counters, in-memory `KeyValueContainerData` statistics, volume used-space counters, and `ContainerChecksumTreeManager`. It depends on `BlockDeletingService`, `OzoneContainer`, container handlers, `BlockUtils`, `KeyValueContainerUtil`, and RocksDB `BatchOperation`.

Risks: File deletion and DB mutation are not one atomic filesystem/DB transaction. A failed chunk delete can leave delete transactions pending. Processed-byte and released-byte accounting diverge for missing/unreferenced blocks. The max lock-hold time can leave partial transaction batches for future runs. Schema v1 relies on key prefix filtering in a shared default table. Marking a container empty depends on `container.hasBlocks()` after deletes.

Test signals: Cover all three schemas, empty/missing data directory, container lock retry exhaustion, missing block metadata, unreferenced files, duplicate local IDs across transactions, DB batch failure after file deletion, checksum tree updates before transaction removal, max lock-hold cutoff, counter/volume decrements, and no-progress loop break.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/BlockDeletingTask.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/StaleRecoveringContainerScrubbingService.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/StaleRecoveringContainerScrubbingService.java

Purpose: Provides a datanode background service that marks stale recovering containers unhealthy after their recovery timeout expires.

Important APIs and functions: The constructor configures the `BackgroundService` name, interval, thread pool, timeout, and `ContainerSet`. `getTasks()` scans the recovering-container iterator, enqueues `RecoveringContainerScrubbingTask` for expired entries, and removes them from the tracking iterator. The task `call()` fetches the container and calls `markContainerUnhealthy()`.

Control flow and state: The service assumes the `ContainerSet` recovering-container iterator is ordered by timeout, because it stops at the first non-expired entry. Tasks carry only container ID and `ContainerSet` reference. Missing containers are silently ignored by the task.

Persistence and dependencies: Marking unhealthy delegates to the container implementation, which persists container state through its metadata file. The service depends on HDDS background task queues and `ContainerSet.RecoveringContainer`.

Risks: Iterator ordering is essential; if entries are unordered, later expired containers can be skipped. Removing entries before task execution means a task failure may lose the pending scrub marker. The task marks any currently loaded container unhealthy without rechecking state or timeout.

Test signals: Cover ordered timeout scanning, first non-expired break behavior, iterator removal, missing containers, marking loaded recovering containers unhealthy, repeated service intervals, and task exceptions under background service timeout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/StaleRecoveringContainerScrubbingService.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/package-info.java

Purpose: Documents the background task package related to the key-value container state machine.

Important APIs and functions: The package includes maintenance services such as block deletion and stale recovering-container scrubbing that run outside foreground write/read request handling.

Control flow and state: This file has no executable flow. It identifies a package boundary for scheduled and asynchronous state-machine maintenance.

Persistence and dependencies: Persistence effects are implemented by task classes that update container metadata, RocksDB tables, chunk files, and volume state. The package-info file has no direct dependencies.

Risks: Background tasks often mutate persistent state after foreground operations enqueue work; keeping them in a clearly documented package helps audit asynchronous side effects.

Test signals: Package compile checks plus behavioral tests on the contained background services.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/statemachine/background/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeDBDefinition.java

Purpose: Defines the common DBDefinition base for datanode container RocksDB schema definitions.

Important APIs and functions: The constructor stores DB path and configuration. `getName()` returns the DB directory name, `getDBLocation()` returns the parent directory, and `getLocationConfigKey()` intentionally throws because datanode container DBs are located by container/volume paths, not a global config key. Abstract accessors define block data, metadata, and last-chunk column families; finalize blocks is optional.

Control flow and state: This class is immutable after construction, carrying `dbDir` and `config`. Concrete schema definitions supply column family names, codecs, and maps.

Persistence and dependencies: It integrates with HDDS `DBDefinition` and `DBColumnFamilyDefinition` and names the column families consumed by `AbstractDatanodeStore`. It does not itself open RocksDB.

Risks: `getDBLocation()` assumes the supplied path includes a parent directory. Concrete schema definitions must return column families with codecs compatible with existing on-disk data. Optional `getFinalizeBlocksColumnFamily()` returning null requires callers to guard.

Test signals: Instantiate each schema with representative paths, assert DB name/location, verify unsupported location config key, and validate column family definitions and nullability by schema.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeStore.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeStore.java

Purpose: Implements common datanode container store behavior over RocksDB: opening schema definitions, wrapping tables, providing safe iterators, and exposing block/finalize iteration.

Important APIs and functions: `initDBStore()` applies schema-specific DB options, builds the DB, initializes metadata, block, finalize, and last-chunk tables, and wraps normal tables in `DatanodeTable` to disable raw iteration. `getBlockIterator()` and `getFinalizeBlockIterator()` return filtering iterators. `checkTableStatus()` fails fast on missing tables. Nested iterators filter keys by `KeyPrefixFilter` and cache the next value.

Control flow and state: The store keeps both wrapped tables for normal point operations and unwrapped iterator-capable tables for controlled iteration. Schema v1/v2 cap total WAL size; schema v3 customizes obsolete file deletion and JMX naming. Iterator classes scan underlying RocksDB iterators and apply byte-level prefix filters before exposing blocks or local IDs.

Persistence and dependencies: Inherits RocksDB lifecycle from `AbstractRDBStore`. Integrates with `DatanodeSchema*DBDefinition`, `DatanodeConfiguration`, `DBStoreBuilder`, `Table`, `BlockData`, `ChunkInfoList`, and container `BlockIterator`.

Risks: Direct table iteration is intentionally disabled except through controlled paths; bypassing this can mix schema prefixes. Iterator `nextBlock()` recurses after `hasNext()`, which is shallow but should remain correct. Missing finalize/last-chunk tables are schema-dependent. Schema v3 prefix filters must align with fixed-length key encoding.

Test signals: Open schema one/two/three stores, verify table wrappers and iterator-capable tables, iterate normal and filtered blocks, iterate finalize local IDs, handle missing tables, enforce unsupported raw iteration, and close/flush/compact through inherited DB manager APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractDatanodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractRDBStore.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractRDBStore.java

Purpose: Provides the generic RocksDB-backed store manager base used by datanode metadata stores.

Important APIs and functions: The constructor selects `DatanodeDBProfile`, reads DB and column-family options from configured files when present, applies create-if-missing and log settings, and delegates DB construction to `initDBStore()`. `stop()`, `close()`, `isClosed()`, `getStore()`, `getBatchHandler()`, `flushDB()`, `flushLog()`, and `compactDB()` implement `DBStoreManager`.

Control flow and state: Each instance owns a `DBDefinition`, shared/default column-family options, and a volatile `DBStore`. `close()` stops the store then closes CF options. `dbProfile` is static, so the last constructed store updates the class-wide profile reference.

Persistence and dependencies: It directly opens and manages RocksDB through HDDS `DBStoreBuilder`, managed RocksDB options, `DBConfigFromFile`, and datanode configuration log settings. Subclasses choose column families and expose typed tables.

Risks: Static `dbProfile` can surprise tests with multiple configurations. File-based RocksDB option parsing failures abort store construction. `cfOptions` is closed on `close()`, so no table should outlive the store. A null options file falls back to profile defaults.

Test signals: Cover construction with default and file-based DB/CF options, read-only open, log level/file settings, close/stop idempotence, flush/compact delegation, DB profile exposure, and option-file exception handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/AbstractRDBStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/ContainerCreateInfo.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/ContainerCreateInfo.java

Purpose: Immutable value object recording a container's creation state and EC replica index for the witnessed-container metadata DB.

Important APIs and functions: `valueOf()` creates instances. `getCodec()`/`getNewCodec()` return a delegated protobuf codec. `getProtobuf()` lazily memoizes the protobuf representation. `getFromProtobuf()`, `getState()`, and `getReplicaIndex()` expose conversion and fields. `INVALID_REPLICA_INDEX` encodes legacy/no-index state.

Control flow and state: Instances hold final state, final replica index, and a memoized supplier for `ContainerProtos.ContainerCreateInfo`. The class is annotated immutable and exposes no mutators.

Persistence and dependencies: Persisted via `DelegatedCodec` over `Proto3Codec` in `WitnessedContainerMetadataStore`. It depends on container protobuf state enums and Ratis `MemoizedSupplier`.

Risks: `getNewCodec()` currently aliases `getCodec()`, so future codec migration must be intentional. Legacy records with invalid replica index require callers to interpret `-1` as no prior EC index. The protobuf supplier memoizes based on construction fields.

Test signals: Codec round trip, protobuf conversion, invalid replica index handling, immutability assumptions, and compatibility with previous string-valued witnessed-container table migration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/ContainerCreateInfo.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DBStoreManager.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DBStoreManager.java

Purpose: Defines the lifecycle and maintenance contract for datanode RocksDB stores.

Important APIs and functions: `stop()` stops the manager, `close()` is inherited from `UncheckedAutoCloseable`, `getStore()` returns the underlying `DBStore`, `getBatchHandler()` exposes batch transaction support, `flushLog()`, `flushDB()`, and `compactDB()` forward maintenance operations, and `isClosed()` reports thread-safe store closure. `compactionIfNeeded()` is an optional no-op hook.

Control flow and state: This is an interface; implementations decide synchronization and resource ownership. It separates generic DB operations from schema-specific table access.

Persistence and dependencies: It is the common contract used by `DatanodeStore` and `WitnessedContainerMetadataStore`, backed by HDDS `DBStore` and `BatchOperationHandler`.

Risks: Callers may assume `compactionIfNeeded()` has effect for every store, but only schema-specific implementations override it. `getStore()` can return null or closed stores depending on implementation lifecycle.

Test signals: Compile all implementors, verify close/stop/flush/compact paths, ensure batch operations are exposed, and test schema-three compaction override through this interface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DBStoreManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaOneDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaOneDBDefinition.java

Purpose: Defines the legacy schema-one datanode container DB layout where block data, metadata, and deleted block records all share RocksDB's default column family.

Important APIs and functions: Static column family definitions `BLOCK_DATA`, `METADATA`, and `DELETED_BLOCKS` all reference the default CF name but use different value codecs. Accessors return those definitions. `getColumnFamilies(String)` and `getColumnFamilies()` expose a multimap so multiple logical tables can map to one physical CF.

Control flow and state: The definition is immutable. Logical table separation is achieved through codecs and key prefixes rather than physical column families.

Persistence and dependencies: Uses `SchemaOneKeyCodec` for mixed long/string keys, `BlockData.getCodec()`, `LongCodec`, and `SchemaOneChunkInfoListCodec`. `DatanodeStoreSchemaOneImpl` wraps the deleted-block table to apply `#deleted#` prefixes.

Risks: Multiple logical tables over one CF can decode unrelated keys with the wrong value codec. Schema-one compatibility depends heavily on key-prefix conventions. Deleted block values may be either old local-ID placeholders or newer chunk-info protobufs.

Test signals: Open existing schema-one DBs, round-trip unprefixed numeric block keys and prefixed metadata/deleted keys, scan deleting blocks, access deleted-block records through the wrapper, and validate mixed logical table definitions on one CF.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaOneDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaThreeDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaThreeDBDefinition.java

Purpose: Defines schema-three datanode DB layout with separate column families and fixed-length container-ID prefixes for shared per-volume RocksDB databases.

Important APIs and functions: Column families cover `block_data`, `metadata`, `delete_txns`, `finalize_blocks`, and `last_chunk_info`, all with fixed-length string keys. `getContainerKeyPrefix()`, `getContainerKeyPrefixBytes()`, `getContainerKeyPrefixLength()`, `getKeyWithoutPrefix()`, and `getContainerId()` encode/decode prefixes. The constructor sets the separator and configures each CF with a fixed-length prefix extractor.

Control flow and state: `separator` is static and set from datanode configuration in the constructor. CF options are read per column family from optional RocksDB config or from the datanode DB profile, then modified for prefix seek.

Persistence and dependencies: Uses `FixedLengthStringCodec`, `LongCodec`, `Proto2Codec` for delete transactions, `BlockData` codecs, HDDS DB definitions, and RocksDB managed CF options. `DatanodeStoreSchemaThreeImpl` relies on these prefixes for per-container iteration, dump/load, delete, and compaction.

Risks: Static separator changes affect all schema-three definitions in the JVM. Prefix length must match fixed-length encoded container IDs plus separator exactly or prefix seek and compaction ranges break. `getKeyWithoutPrefix()` uses the first separator occurrence, so separator choice must not conflict with encoded prefixes.

Test signals: Validate key prefix round trips, container ID extraction from smallest/largest SST keys, prefix bytes length, per-CF prefix extractor setup, custom options-file handling, delete transaction key encoding, and iteration constrained to one container.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaThreeDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaTwoDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaTwoDBDefinition.java

Purpose: Defines schema-two datanode container DB layout with separate physical column families for block data, metadata, delete transactions, finalized blocks, and last-chunk information.

Important APIs and functions: Static column family definitions include `BLOCK_DATA`, `METADATA`, `DELETE_TRANSACTION`, `FINALIZE_BLOCKS`, and `LAST_CHUNK_INFO`. `getMap()` exposes the DBDefinition map. Accessors return each schema component, with delete transactions keyed by `Long`.

Control flow and state: The definition is immutable and per container DB path. Unlike schema three, schema two does not prefix every key with container ID because each DB belongs to one container.

Persistence and dependencies: Uses `StringCodec` for block/metadata keys, `LongCodec` for transaction IDs and values, `FixedLengthStringCodec` for finalized blocks and last-chunk records, `Proto2Codec` for `DeletedBlocksTransaction`, and `BlockData` codecs.

Risks: Delete transaction keys are only transaction IDs, so schema-two stores must not be shared across containers. Mixing fixed-length and normal string codecs by table means callers must route keys to the correct table. Last-chunk table availability is required for incremental chunk list support.

Test signals: Open schema-two DBs, put/get/delete transactions by long ID, finalized block iteration, last-chunk incremental writes, block data CRUD, and migration behavior from schema one where relevant.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeSchemaTwoDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStore.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStore.java

Purpose: Defines the typed table and block access contract for datanode container metadata stores.

Important APIs and functions: Accessors expose block data, metadata, deleted blocks, finalize blocks, and last-chunk tables. Iterators expose block and finalize-block traversal with optional filters. `getBlockByID()` fetches block data by key and delegates to `getCompleteBlockData()`. `putBlockByID()` has a default old-client behavior that overwrites the block data table.

Control flow and state: This interface extends `DBStoreManager`. Default methods encode common block lookup/update behavior while allowing incremental chunk-list stores to override completion and put logic.

Persistence and dependencies: Tables are RocksDB-backed through HDDS `Table`. It integrates `BlockID`, `BlockData`, `ChunkInfoList`, `BatchOperation`, `KeyValueContainerData`, and `KeyPrefixFilter`.

Risks: `getDeletedBlocksTable()` exists for schema one compatibility but is unsupported in base schema-two/three implementations. Default `getCompleteBlockData()` throws `NO_SUCH_BLOCK` for null data; incremental stores may recover data from last-chunk table. Batch callers must commit through the store's batch handler.

Test signals: Table access for each schema, default block missing exception, incremental override behavior, batch put by local ID, filtered block iteration, finalize-block iteration, and deleted-block table support only for schema one.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaOneImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaOneImpl.java

Purpose: Opens and exposes a schema-one datanode store, preserving logical deleted-block table access over the legacy default column family.

Important APIs and functions: The constructor builds an `AbstractDatanodeStore` with `DatanodeSchemaOneDBDefinition`, then obtains and checks the deleted-block logical table. `getDeletedBlocksTable()` returns a `SchemaOneDeletedBlocksTable` wrapper that adds/removes the schema-one deleted prefix.

Control flow and state: The store inherits block and metadata table setup from the abstract base and maintains a `deletedBlocksTable` field for schema-one-specific access.

Persistence and dependencies: All logical data is persisted in RocksDB's default CF with schema-one codecs. It depends on `DatanodeTable`, `SchemaOneDeletedBlocksTable`, and `ChunkInfoList`.

Risks: Each `getDeletedBlocksTable()` call creates a new wrapper; this is cheap but means object identity is not stable. Prefix handling must be centralized in the wrapper so callers do not double-prefix. Value decoding may return null for old deleted-block records without chunk info.

Test signals: Construct schema-one stores, use deleted-block put/get/delete/range without caller prefixes, verify physical `#deleted#` storage, access normal block/metadata tables, and close/read-only open behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaOneImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaThreeImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaThreeImpl.java

Purpose: Implements schema-three container metadata storage over shared, container-prefixed RocksDB tables, including delete transaction access, per-container export/import, removal, iteration, and small-SST compaction.

Important APIs and functions: `getDeleteTransactionTable()` exposes string-keyed delete transactions. `getBlockIterator()` and `getFinalizeBlockIterator()` constrain iterators by container prefix. `removeKVContainerData()` deletes all prefixed rows for a container in one batch. `dumpKVContainerData()` and `loadKVContainerData()` export/import SST files per table. `compactionIfNeeded()` scans live SST metadata and compacts ranges with too many small files.

Control flow and state: The store inherits incremental chunk-list behavior. Dump/load process metadata, block data, optional last-chunk data gated by layout feature finalization, and delete transactions. Compaction groups live files by column family and level, computes min/max container IDs for small files, then compacts a prefix range.

Persistence and dependencies: Persists to schema-three column families using fixed-length prefixed keys. Depends on RocksDB live file metadata, SST file readers, compact range options, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.HBASE_SUPPORT`, and `DatanodeSchemaThreeDBDefinition` prefix helpers.

Risks: Prefix delete/dump/load affects all rows with a container prefix; prefix encoding bugs can remove another container's data. Loading SST dumps decodes every key/value and batches puts, so malformed dump files fail import. Compaction range `endCId + 1` must avoid overflow. Missing empty dump files are treated as no-op.

Test signals: Per-container iteration isolation, delete transaction CRUD, remove all prefixed data, dump/load round trip including empty files, HBASE_SUPPORT on/off last-chunk handling, small-SST compaction thresholds, unknown CF warning, and import failure on corrupt SST data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaThreeImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaTwoImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaTwoImpl.java

Purpose: Opens and exposes schema-two datanode stores with incremental chunk-list support and long-keyed delete transactions.

Important APIs and functions: The constructor builds `DatanodeStoreWithIncrementalChunkList` using `DatanodeSchemaTwoDBDefinition`, then retrieves the delete transactions table. `getDeleteTransactionTable()` returns `Table<Long, DeletedBlocksTransaction>`.

Control flow and state: The implementation carries only the delete transaction table field beyond inherited table state. Block data, metadata, finalize, and last-chunk table setup is inherited.

Persistence and dependencies: Persists delete transactions in the `delete_txns` CF using `LongCodec` keys and protobuf values. Inherits block/metadata persistence and incremental chunk handling.

Risks: Because delete transactions are not container-prefixed, schema-two DBs must remain one DB per container. Table status is not explicitly checked here after retrieval, so DBDefinition/store build correctness is important. Delete task casts this store through `DeleteTransactionStore<Long>`.

Test signals: Store construction, delete transaction put/get/delete/range through block deletion, incremental chunk list writes, finalized block table use, read-only open, and schema-two block deletion flow.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreSchemaTwoImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreWithIncrementalChunkList.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreWithIncrementalChunkList.java

Purpose: Extends the datanode store to support incremental chunk-list updates where the latest partial chunk is stored separately until it becomes complete or the block ends.

Important APIs and functions: `getCompleteBlockData()` merges block data and last-chunk info. `reconcilePartialChunks()` validates offsets and appends the saved partial chunk. `putBlockByID()` routes old-client/full writes to the block table, full/eob incremental updates through `moveLastChunkToBlockData()`, and partial updates through `putBlockWithPartialChunks()`.

Control flow and state: Incremental blocks are identified by `INCREMENTAL_CHUNK_LIST` metadata. A full last chunk or end-of-block moves accumulated partial data into the main block table and deletes last-chunk state. A non-final partial write updates the last-chunk table and may insert an empty block entry for compatibility with utilities expecting block-table presence.

Persistence and dependencies: Uses the main block data table and `last_chunk_info` table in schema two/three. Depends on `BlockManagerImpl.FULL_CHUNK` metadata, `KeyValueContainerData` key generation, `BlockData`, and protobuf chunk metadata.

Risks: Offset validation is strict and throws if the saved partial chunk does not follow the block table's last full chunk. Mutating `BlockData` chunk lists in place can surprise callers holding references. The compatibility empty block entry has metadata but no chunks. Missing last-chunk table would break this class.

Test signals: Old-client overwrite, first partial chunk, repeated partial replacement, multiple chunks with final partial, full last chunk promotion, end-of-block promotion with empty data, missing block plus last-chunk lookup, offset mismatch failure, and BCSID propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeStoreWithIncrementalChunkList.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeTable.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeTable.java

Purpose: Wraps an HDDS `Table` for datanode container stores while disabling direct iteration to prevent schema-unsafe scans.

Important APIs and functions: Most CRUD, batch, range, prefix-delete, dump, and load methods delegate to the wrapped table. `iterator(KEY prefix, IteratorType type)` is final and throws `UnsupportedOperationException`. `getName()`, estimated counts, existence checks, and read-copy operations are pass-throughs.

Control flow and state: The class holds a single wrapped `Table` reference. It enforces iteration policy at runtime while allowing controlled iterators to use separate unwrapped table handles inside `AbstractDatanodeStore`.

Persistence and dependencies: It does not add persistence behavior; it delegates to RocksDB-backed table implementations. It depends on HDDS table, batch, codec, iterator type, and metadata key filter abstractions.

Risks: New `Table` methods must be delegated or deliberately blocked when the interface evolves. Code that requires iteration must obtain schema-aware iterators from `DatanodeStore`, not this wrapper. Since prefix-delete and dump are still delegated, callers must pass schema-correct prefixes.

Test signals: Verify put/get/delete/batch/range delegation, direct iterator failure, prefix delete and dump delegation, table name/count pass-through, and schema-aware iterator access through store APIs.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DatanodeTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DeleteTransactionStore.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DeleteTransactionStore.java

Purpose: Small schema-neutral interface for stores that expose a delete transaction table.

Important APIs and functions: `getDeleteTransactionTable()` returns `Table<TXN_KEY, DeletedBlocksTransaction>`, where the key type is schema-specific: `Long` for schema two and `String` for schema three.

Control flow and state: The interface is stateless and used for casts by block deletion code after schema dispatch.

Persistence and dependencies: It abstracts the RocksDB delete transaction column family that stores SCM delete transactions until chunks and block metadata are removed.

Risks: Callers must choose the correct generic key type for the schema. A wrong cast would fail at runtime or delete the wrong transaction key. Schema one does not implement this interface because it uses deleting block key prefixes instead of transaction tables.

Test signals: Compile-time coverage for schema-two and schema-three implementations, block deletion casts by schema, transaction table CRUD, and unsupported schema-one path avoiding this interface.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/DeleteTransactionStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneChunkInfoListCodec.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneChunkInfoListCodec.java

Purpose: Provides a schema-one-compatible codec for deleted-block values that may contain either modern chunk info protobufs or legacy non-protobuf placeholders.

Important APIs and functions: `get()` returns the singleton codec. `toPersistedFormat()` serializes `ChunkInfoList` protobuf bytes. `fromPersistedFormat()` attempts to parse `ContainerProtos.ChunkInfoList`; on parse failure it logs a warning once and returns null. `copyObject()` is unsupported.

Control flow and state: The codec has singleton state and an `AtomicBoolean LOGGED` to avoid repeated warnings for legacy data. Decode failure is not thrown to callers; it returns null to reflect absent chunk information.

Persistence and dependencies: Used by schema-one deleted-block logical table over the default CF. Depends on container protobufs, `ChunkInfoList`, HDDS `Codec`, and protobuf parse exceptions.

Risks: Returning null for invalid data requires callers to tolerate absent chunk info. `copyObject()` unsupported can break generic code that assumes all codecs copy. Parse failure could also indicate corruption, not just legacy format, but the codec treats both as missing chunk info.

Test signals: Encode/decode valid chunk lists, decode legacy long/random bytes to null with one warning, verify singleton behavior, and ensure deleted-block table users handle null values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneChunkInfoListCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneDeletedBlocksTable.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneDeletedBlocksTable.java

Purpose: Adapts schema-one deleted-block operations to look like an unprefixed logical table while storing keys with `#deleted#` in the shared default column family.

Important APIs and functions: Overrides put, batch put, delete, batch delete, delete range, existence, get, read-copy, and range methods to prefix keys before delegation. `getRangeKVs()` ignores caller filters and uses the deleted-key filter, then strips prefixes from returned keys.

Control flow and state: The class extends `DatanodeTable` and has no mutable state beyond the wrapped table. Prefix/unprefix helpers handle nulls and remove the first deleted prefix.

Persistence and dependencies: It persists `ChunkInfoList` values through the schema-one default CF. It uses `KeyPrefixFilter.newFilter("#deleted#")` to prevent regular block keys from being returned as deleted blocks.

Risks: `String.replaceFirst()` treats the prefix as a regex; the current prefix is safe but future special characters would matter. Ignoring user-supplied range prefixes is intentional but can surprise callers. Double-prefixing by callers would produce bad physical keys.

Test signals: Put/get/delete with unprefixed keys, range scans returning unprefixed keys, delete range, null key handling, collision with non-deleted block keys, and caller-supplied prefix/filter ignored for deleted table scans.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneDeletedBlocksTable.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneKeyCodec.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneKeyCodec.java

Purpose: Encodes and decodes schema-one keys that historically mixed binary long block IDs and string metadata/prefixed keys in the same RocksDB column family.

Important APIs and functions: `toPersistedFormat()` encodes parseable numeric strings as `LongCodec`, otherwise as `StringCodec`. `fromPersistedFormat()` decodes bytes as string first, recognizes known metadata/prefixed block regexes, otherwise decodes 8-byte arrays as longs and all other arrays as strings. `copyObject()` returns the same immutable string.

Control flow and state: Singleton codec with trace logging for format decisions. Regexes distinguish keys like `#deleted#123` and short metadata keys from numeric block IDs.

Persistence and dependencies: Used by all schema-one logical column families. It depends on HDDS long/string codecs and is central to reading pre-codec schema-one DBs.

Risks: Ambiguous byte arrays can decode as a string if their string representation matches known regexes, even if originally a long. Numeric metadata-like strings without prefixes are stored as longs. Regex coverage must match every schema-one string key pattern.

Test signals: Round-trip numeric block IDs, metadata keys, deleted/deleting prefixes, non-8-byte strings, ambiguous 8-byte payloads, trace decision paths, and compatibility with existing schema-one RocksDB data.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/SchemaOneKeyCodec.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerDBDefinition.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerDBDefinition.java

Purpose: Defines the master-volume RocksDB schema that records containers witnessed on a datanode.

Important APIs and functions: Singleton `get()` returns the DB definition. `CONTAINER_CREATE_INFO_TABLE_DEF` maps `ContainerID` keys to `ContainerCreateInfo` values in `ContainerCreateInfoTable`. `getName()` returns the witnessed-container DB name. `getLocationConfigKey()` points to the datanode ID directory configuration. Package-private `getContainerCreateInfoTableDef()` exposes the table definition to the store implementation.

Control flow and state: The class extends `DBDefinition.WithMap` with one immutable column family map and a singleton instance.

Persistence and dependencies: Uses `ContainerID.getCodec()`, `ContainerCreateInfo.getCodec()`, SCM config keys, and `OzoneConsts.WITNESSED_CONTAINER_DB_NAME`. `WitnessedContainerMetadataStoreImpl` opens and reads this definition.

Risks: The location is global to the datanode identity/master volume rather than individual container volumes. Table definition visibility is package-private, so schema changes must be coordinated in the metadata package.

Test signals: DBDefinition name/location resolution, table codec round trip, singleton behavior, opening store through `WitnessedContainerMetadataStoreImpl`, and upgrade compatibility with previous table name.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerDBDefinition.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStore.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStore.java

Purpose: Defines typed access to the witnessed-container metadata DB in the datanode master volume.

Important APIs and functions: Extends `DBStoreManager` and adds `getContainerCreateInfoTable()`, returning a table of `ContainerID` to `ContainerCreateInfo`.

Control flow and state: This is an interface. Implementations can choose the current protobuf-valued table or a previous-version compatibility table depending on upgrade finalization state.

Persistence and dependencies: The table is used by container loading to remember the last loaded container creation state and EC replica index. It depends on HDDS `Table` and SCM `ContainerID`.

Risks: Callers must use the interface instead of assuming a specific physical table, because upgrades can route to a legacy string-valued table. Incorrect witnessed metadata can cause EC container loads to be ignored.

Test signals: Compile users, access table before and after upgrade finalization, write/read `ContainerCreateInfo`, and validate `ContainerReader` behavior when DB replica index differs from on-disk container replica index.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStoreImpl.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStoreImpl.java

Purpose: Implements the witnessed-container metadata store, including singleton-per-DB-path reuse and upgrade compatibility for the old string-valued container IDs table.

Important APIs and functions: Static `get()` computes the DB directory path and returns a cached open store or creates one. `initDBStore()` adds previous-version tables when needed, builds the DB, initializes compatibility tables, and opens the current `ContainerCreateInfoTable`. `getContainerCreateInfoTable()` returns the legacy table until `WITNESSED_CONTAINER_DB_PROTO_VALUE` is finalized. Nested `PreviousVersionTables` wires the old `containerIds` table through a delegated codec.

Control flow and state: A concurrent map caches stores by DB directory. Store initialization is layout-feature dependent. The compatibility codec maps old string state names to `ContainerCreateInfo` with invalid replica index and writes back state names when using the old table.

Persistence and dependencies: Inherits RocksDB lifecycle from `AbstractRDBStore`. Depends on `DBStoreBuilder`, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.WITNESSED_CONTAINER_DB_PROTO_VALUE`, `ContainerID`, `ContainerCreateInfo`, and delegated codecs.

Risks: Cached stores can outlive configuration expectations if DB paths collide. Layout finalization state controls which table is active; changing state across a running process must be coordinated. Legacy records lack replica index, so EC matching treats them as no prior index.

Test signals: Concurrent `get()` reuse, closed store recreation, current table access after finalization, legacy table access before finalization, delegated codec mapping for old states, DB close/isClosed behavior, and `ContainerReader` integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/WitnessedContainerMetadataStoreImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/package-info.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/package-info.java

Purpose: Documents the datanode metadata package as the place where database structure and read/write access classes live.

Important APIs and functions: The package contains schema definitions, store implementations, table wrappers, codecs, delete transaction abstractions, and witnessed-container metadata DB classes.

Control flow and state: This file has no runtime behavior. It describes the package boundary for RocksDB metadata used by containers and datanode-level witnessed-container state.

Persistence and dependencies: Persistent behavior in the package covers container block metadata, counters, delete transactions, last-chunk records, finalized blocks, and witnessed container create info. This file itself has no imports.

Risks: Because this package owns multiple schema versions and upgrade compatibility, documentation should remain explicit that both DB structure and access helpers belong here.

Test signals: Package compile and documentation checks; schema/store/codec behavior is covered by the individual classes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/metadata/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractBackgroundContainerScanner.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractBackgroundContainerScanner.java

Purpose: Base runnable for scheduled datanode container scanners, handling thread lifecycle, iteration cadence, pause/unpause, shutdown, and common metrics reset/logging.

Important APIs and functions: `start()` starts the daemon scanner thread. `run()` loops `runIteration()` until stopping and unregisters metrics on exit. `runIteration()` optionally scans, logs metrics, resets per-iteration gauges, and sleeps for the remaining interval. `scanContainers()` iterates containers and invokes subclass `scanContainer()`. `shutdown()`, `pause()`, `unpause()`, and `isAlive()` manage lifecycle.

Control flow and state: Atomic flags track stopping and pausing. Each iteration computes elapsed time and sleeps only the remaining configured interval. Interrupted scan operations set stopping. Subclasses supply container iterator, scan behavior, and metrics.

Persistence and dependencies: No direct persistence, but subclasses call container scan methods that can mark containers unhealthy or update checksums. Depends on `Container` and `AbstractContainerScannerMetrics`.

Risks: Any unchecked exception exits the scanner thread. Metrics are reset after every run-loop iteration, so consumers observe per-iteration gauges. Shutdown joins the thread and can block until scan code honors interruption. Pause only takes effect between container scans, not inside a long container scan.

Test signals: Start/run/shutdown behavior, pause skipping scans, interrupt handling, sleep duration calculation, metrics increment/reset/unregister, exception exit, and subclass scan invocation order.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractBackgroundContainerScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractContainerScannerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractContainerScannerMetrics.java

Purpose: Defines shared Hadoop Metrics2 counters and gauges for container scanners.

Important APIs and functions: Tracks current-iteration containers scanned, current-iteration unhealthy containers, and total scan iterations since restart. Increment, getter, and reset methods wrap `MutableGaugeInt` and `MutableCounterInt`. `unregister()` removes the metrics source, and `getName()` exposes its name.

Control flow and state: Subclasses register concrete instances with a `MetricsSystem`, then this base owns the mutable metric fields injected by Metrics2. Reset methods decrement gauges by their current value.

Persistence and dependencies: Metrics are in-memory telemetry, not persistent state. Depends on Hadoop Metrics2 annotations, `MetricsSystem`, and mutable metric types.

Risks: Reset-by-decrement assumes no concurrent increments during reset. `unregister()` must be called once scanner lifecycle ends to avoid duplicate source registration. Metrics fields are initialized by Metrics2 registration, so manual construction without registration can leave null fields.

Test signals: Metrics registration, increments and resets, unregister on scanner shutdown, subclass metric inheritance, duplicate registration names, and concurrent scan metric updates if scanners become multi-threaded.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/AbstractContainerScannerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerDataScanner.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerDataScanner.java

Purpose: Per-volume background scanner that performs full data scans of containers on one HDDS volume with bandwidth throttling and cancellation.

Important APIs and functions: The constructor binds a volume, controller, throttler, canceler, metrics, and `ContainerScanHelper`. `scanContainer()` shuts down if the volume failed, otherwise delegates to `scanHelper.scanData()`. `getContainerIterator()` returns containers for the volume. `shutdown()` cancels the throttler/canceler and stops the base scanner. Nested `HddsDataTransferThrottler` increments byte-scan metrics.

Control flow and state: One daemon scanner thread runs per volume via the base class. Volume failure triggers scanner shutdown. Throttler methods are synchronized and count bytes before delegating to Hadoop throttling.

Persistence and dependencies: Data scans can update container checksums, scan timestamps, and unhealthy state through `ContainerScanHelper` and `ContainerController`. Depends on `HddsVolume`, `DataTransferThrottler`, `Canceler`, and data scanner metrics.

Risks: A failed volume stops its scanner permanently. Canceling during shutdown depends on scan code observing the canceler. Metrics count requested throttled bytes, not necessarily successfully read bytes. The scanner uses configured minimum scan gaps through the helper.

Test signals: Per-volume iterator filtering, shutdown on failed volume, throttling byte metrics, canceler interruption, scan gap behavior, checksum/timestamp update after data scan, and thread shutdown/join.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerDataScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerMetadataScanner.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerMetadataScanner.java

Purpose: Single background scanner that verifies metadata for all loaded containers across volumes.

Important APIs and functions: The constructor sets the metadata scan interval, controller, metrics, and scan helper. `getContainerIterator()` iterates all containers through `ContainerController`. `scanContainer()` delegates to `scanHelper.scanMetadata()`. `getMetrics()` returns metadata scanner metrics.

Control flow and state: Inherits thread lifecycle, pause, and sleep behavior from `AbstractBackgroundContainerScanner`. Unlike data scanning, there is one scanner for all volumes.

Persistence and dependencies: Metadata scans can mark containers unhealthy and trigger volume failure scans but do not update data scan timestamps. Depends on `ContainerController`, `ContainerScanHelper`, and `ContainerMetadataScannerMetrics`.

Risks: A slow or stuck metadata scan blocks scanning for all volumes. The same min scan gap used by the helper can skip recently data-scanned containers. Exceptions per container are caught by the base scanner, but unchecked helper failures can exit the thread.

Test signals: Iterate all containers, skip failed-volume/recently-scanned containers, mark unhealthy metadata errors, transient too-many-open-files handling, metrics increment/reset, and scanner lifecycle.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/BackgroundContainerMetadataScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerController.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerController.java

Purpose: Acts as the datanode control-plane facade for container lookup, state transitions, reports, import/export/copy/delete, reconciliation, scanner updates, and handler dispatch.

Important APIs and functions: Exposes container lookup/location, close/quasi-close/mark-for-close, `markContainerUnhealthy()`, checksum updates, reports, finalized block recording/checking, import/copy/export/delete, reconciliation, iteration by all containers or volume, volume container counts, and data scan timestamp updates.

Control flow and state: The controller holds a `ContainerSet` and a map from container type to `Handler`. Most operations fetch the container, choose the handler by type, and delegate. Export failures trigger an on-demand container scan through `ContainerSet.scanContainer()` before rethrowing. Missing containers are logged and often treated as skipped except close paths that throw.

Persistence and dependencies: Persistence occurs inside handlers and containers: state files, checksums, data scan timestamps, and container reports. Integrates with `DNContainerOperationClient`, `ContainerMerkleTreeWriter`, `TarContainerPacker`, and HDDS container protobuf/report types.

Risks: `getHandler(container)` assumes non-null container and registered handler. Several methods do not guard null containers before handler calls. Missing-container behavior differs by operation. Export failure scanning is side-effectful. Package-private `updateDataScanTimestamp()` is used by scanner helpers.

Test signals: Handler dispatch for each operation, missing container close versus mark unhealthy/update checksum behavior, export failure scan trigger, finalized block APIs, per-volume iteration/count, reconciliation delegation, and null/unregistered handler failure modes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerController.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerDataScannerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerDataScannerMetrics.java

Purpose: Metrics source for per-volume background container data scanners.

Important APIs and functions: `create(volumeName)` registers a uniquely named Metrics2 source. `incNumBytesScanned()` records scanner bandwidth through a `MutableRate`. Mean, sample count, and standard deviation getters expose scan bandwidth statistics. `getStorageDirectory()` and `setStorageDirectory()` publish the scanned volume directory.

Control flow and state: Extends the shared scanner metrics base. Empty volume names receive a random suffix to avoid duplicate metrics names. Colons in volume names are replaced for metric source naming.

Persistence and dependencies: In-memory telemetry only. Depends on `DefaultMetricsSystem`, `MutableRate`, and thread-local random for fallback names.

Risks: Volume path-based names can still collide after character replacement. `ThreadLocalRandom` fallback makes names non-deterministic for empty volume names. Rate statistics reflect throttler calls, not necessarily verified bytes.

Test signals: Metrics registration by volume name, empty-name fallback, byte rate updates, storage directory metric, inherited container/unhealthy/iteration counters, and unregister during scanner shutdown.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerDataScannerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerMetadataScannerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerMetadataScannerMetrics.java

Purpose: Metrics source for the singleton background container metadata scanner.

Important APIs and functions: `create()` registers `ContainerMetadataScannerMetrics` with the default metrics system and inherits scanner counters from `AbstractContainerScannerMetrics`.

Control flow and state: The class adds no metrics beyond the base counters. Its constructor is private so callers use the registered factory.

Persistence and dependencies: In-memory Hadoop Metrics2 telemetry only. Depends on `DefaultMetricsSystem`.

Risks: The fixed source name means only one metadata scanner metrics instance should be registered at a time. Tests must unregister to avoid duplicate source conflicts.

Test signals: Create/register/unregister, inherited counter increments/resets, duplicate creation behavior, and metadata scanner lifecycle integration.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerMetadataScannerMetrics.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerReader.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerReader.java

Purpose: Reads container metadata from an HDDS volume at datanode startup/load time, reconstructs in-memory container state, verifies layout, handles stale/deleted containers, and resolves duplicates.

Important APIs and functions: `run()` reads a volume and marks it failed on fatal errors. `readVolume()` finds cluster/current/container directories and calls `verifyContainerFile()`. `verifyAndFixupContainerData()` parses key-value container data, handles RECOVERING/DELETED state, matches EC replica index with witnessed metadata, adds containers, commits space, and resolves duplicates. `resolveDuplicate()` chooses between duplicate Ratis containers by CLOSED state and BCSID. `cleanupContainer()` removes persistent container data and calls `delete()`.

Control flow and state: The reader is bound to one `HddsVolume`, `ContainerSet`, config, volume set, and `shouldDelete` flag. It supports old SCM ID directories before SCM HA finalization. Recovering Ratis containers may be deleted, while EC recovering containers are marked unhealthy and loaded. Duplicate EC containers are left on disk with first loaded winning.

Persistence and dependencies: Reads `.container` YAML files, parses KV metadata, opens witnessed-container DB for EC matching, updates committed volume space, removes stale/deleted container directories/DB rows through `KeyValueContainerUtil`, and mutates `ContainerSet`.

Risks: Directory scanning catches broad throwables per container and can skip corrupt containers. Duplicate resolution deletes one copy for Ratis containers based on state/BCSID, so bad metadata can remove the desired copy. EC matching can ignore an on-disk container if witnessed DB replica index differs. `shouldDelete` heavily changes behavior.

Test signals: Empty/unformatted volume, old SCM ID directory, missing cluster ID dir, missing/corrupt `.container` file, KV parse fixups, recovering/deleted handling with `shouldDelete`, EC replica index mismatch, duplicate Ratis and EC containers, commit/release space, and volume failure on top-level errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanError.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanError.java

Purpose: Captures a specific scanner-detected container health error with failure type, affected file, and exception.

Important APIs and functions: `FailureType` enumerates missing directories/files, corrupt metadata/chunks, missing or inconsistent data files, inaccessible DB, and write failure. Constructor stores failure, file, and exception. Getters expose fields and `toString()` formats the error.

Control flow and state: Immutable after construction, except the referenced exception object may be mutable. Used inside `MetadataScanResult` and `DataScanResult` error lists.

Persistence and dependencies: No persistence. Errors are consumed by scanner helpers and container state handlers to mark containers unhealthy and log details.

Risks: Failure type granularity drives operational response; missing a category can force generic handling. The constructor accepts `Exception` but field type is `Throwable`, so callers with non-Exception throwables cannot pass them without wrapping. `toString()` may include verbose exception text.

Test signals: Construct each failure type, verify getters/toString, propagate through metadata/data scan results, and ensure scanner helper logs and unhealthy marking include error details.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanError.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanHelper.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanHelper.java

Purpose: Shared scanner logic used by background and on-demand scanners for deciding whether to scan, running metadata/data scans, updating checksums/timestamps, handling unhealthy results, and triggering volume scans.

Important APIs and functions: `withScanGap()` and `withoutScanGap()` create helpers. `scanData()` checks eligibility, runs `container.scanData()`, handles deleted/transient results, updates container checksum, marks unhealthy if needed, increments metrics, and updates data scan timestamp. `scanMetadata()` performs metadata-only logic. `handleUnhealthyScanResult()` suppresses transient file-descriptor failures, marks containers unhealthy, increments metrics, and calls `triggerVolumeScan()`. `shouldScanMetadata()` and `shouldScanData()` enforce null, failed-volume, min-gap, and container eligibility checks.

Control flow and state: The helper holds logger, controller, metrics, and min scan gap. Recent scan detection compares current time with optional last data scan time. Transient "Too many open files" errors are identified by `ScanTransientIOUtil` and do not mark containers unhealthy or update completion metrics.

Persistence and dependencies: Data scans can persist container checksum updates and data scan timestamps through `ContainerController`. Unhealthy marking persists container state through handlers. Volume scan trigger reports volume failure via `StorageVolumeUtil.onFailure()`.

Risks: Metadata scans also use last data scan time for min-gap suppression. A checksum update failure is logged but does not prevent unhealthy marking or scan completion accounting. Transient failure classification controls whether corruption is ignored. `triggerVolumeScan()` intentionally marks the volume suspect when a container is corrupt.

Test signals: Null/failed-volume/recent scan skips, open container metadata-only on demand, data scan deleted result, transient FD exhaustion, checksum update success/failure, unhealthy marking already unhealthy versus newly unhealthy, timestamp update, metrics increments, and volume scan trigger.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScanHelper.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScannerConfiguration.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScannerConfiguration.java

Purpose: Defines configuration keys, defaults, validation, and accessors for datanode container scrub/scanner behavior.

Important APIs and functions: Config fields include global scanner enablement, developer data/metadata scanner toggles, metadata scan interval, data scan interval, background and on-demand bandwidth per volume, and minimum per-container scan gap. `validate()` resets negative values to defaults and logs warnings. Setters/getters expose selected fields for tests and runtime config injection.

Control flow and state: Annotated with `@ConfigGroup(prefix = "hdds.container.scrub")`; fields are populated by the HDDS config system and validated after construction. Defaults are 3h metadata interval, 7d data interval, 5 MB/s bandwidth, and 15m min gap.

Persistence and dependencies: Configuration is not persisted here. It controls scanner scheduling, throttling, and scan skipping in `BackgroundContainer*Scanner`, `OnDemandContainerScanner`, and `ContainerScanHelper`.

Risks: Constant names for developer toggles include both `DEV_DATA_ENABLED` strings and config keys with `.dev.data.scan.enabled`; callers should use the annotated keys. Negative min-gap warning logs the key constant as default in one message but sets the numeric default. Runtime changes after scanner construction may not affect already-created helpers/throttlers.

Test signals: Config binding, default values, negative validation for all numeric fields, enabled/toggle getters, scan interval setters, min-gap setter, and scanner construction consuming intervals/bandwidth.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/ContainerScannerConfiguration.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/DataScanResult.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/DataScanResult.java

Purpose: Represents a full container data scan result, including metadata/data errors and the container Merkle tree observed during the scan.

Important APIs and functions: `unhealthyMetadata()` converts a failed metadata scan into a data scan result with an empty tree. `deleted()` returns an interned deleted result. `fromErrors()` builds a result with supplied errors and tree. `getDataTree()` exposes the checksum tree writer.

Control flow and state: Extends `MetadataScanResult` and adds final `ContainerMerkleTreeWriter` state. The deleted result is interned because it has no per-scan data; healthy results are not interned because each has its own tree.

Persistence and dependencies: The result itself is not persistent, but `ContainerScanHelper` uses the tree to update container checksum metadata. Depends on Guava preconditions and `ContainerMerkleTreeWriter`.

Risks: `unhealthyMetadata()` requires the metadata result to have errors; using it with healthy/deleted results is invalid. Empty tree for metadata failure intentionally signals no data was scanned. The tree object must reflect exactly the bytes scanned before checksum persistence.

Test signals: Healthy/error/deleted result construction, unhealthy metadata conversion precondition, tree propagation to controller updates, deleted interning, and helper behavior for transient/non-transient data errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/DataScanResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/MetadataScanResult.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/MetadataScanResult.java

Purpose: Represents the result of a container metadata scan, including errors or a deleted-container signal.

Important APIs and functions: `fromErrors()` returns an interned healthy result for empty error lists or a new error result. `deleted()` returns an interned deleted result. `isDeleted()`, `hasErrors()`, and `getErrors()` implement `ScanResult`. `toString()` summarizes healthy, deleted, single-error, and multi-error states.

Control flow and state: Immutable fields hold the error list reference and deleted flag. Common healthy and deleted cases are static singletons.

Persistence and dependencies: No persistence. Consumed by `ContainerScanHelper` to decide unhealthy marking and by `DataScanResult.unhealthyMetadata()` when data scans abort early.

Risks: The constructor stores the list reference without copying; callers should provide immutable or stable lists. A deleted result has no errors and is handled separately from healthy. `toString()` only includes the first error for multi-error summaries.

Test signals: Empty and non-empty error lists, deleted result, immutable list expectations, `ScanResult` contract, toString variants, and scanner helper branching on deleted/errors.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/MetadataScanResult.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandContainerScanner.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandContainerScanner.java

Purpose: Provides single-threaded on-demand container scans triggered by failures or explicit requests, with duplicate scheduling suppression and optional scan-gap bypass.

Important APIs and functions: The constructor creates on-demand throttler, canceler, metrics, executor, scheduled-container set, and helpers with/without gap. `scanContainer()` queues a scan subject to min-gap. `scanContainerWithoutGap()` queues regardless of recent scan time. `performOnDemandScan()` chooses data scan when eligible, otherwise metadata scan. `shutdown()` unregisters metrics, cancels scans, shuts down the executor, waits up to five seconds, and force-stops if needed.

Control flow and state: A concurrent key set prevents multiple queued/running scans for the same container ID. The executor is single-threaded, so scans serialize. The scheduled ID is removed after `performOnDemandScan()` returns.

Persistence and dependencies: Scans can update checksums, timestamps, unhealthy state, and volume failure signals through `ContainerScanHelper`. Depends on `ExecutorService`, `Future`, `DataTransferThrottler`, `Canceler`, and on-demand scanner metrics.

Risks: If `performOnDemandScan()` throws an unchecked exception, the scheduled-container ID removal is skipped because it is not in a finally block. `scanContainer()` calls `shouldScanMetadata()` before duplicate suppression, so recent scans return empty without noting an already scheduled scan. Single-threading limits concurrency under many requests.

Test signals: Queue accepted/rejected duplicate scans, scan-gap and no-gap paths, open-container metadata-only behavior, closed/quasi-closed data scan behavior through `shouldScanData()`, unchecked exception cleanup risk, shutdown cancellation, and forced executor shutdown timeout.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandContainerScanner.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandScannerMetrics.java -->
## sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandScannerMetrics.java

Purpose: Metrics source for the on-demand container scanner.

Important APIs and functions: `create()` registers a source named `On-demand container scanner metrics` and inherits scanner counters from `AbstractContainerScannerMetrics`.

Control flow and state: No additional fields beyond the base metrics. Constructor is private to enforce Metrics2 registration through the factory.

Persistence and dependencies: In-memory Metrics2 telemetry only. Used by `OnDemandContainerScanner` and unregistered during scanner shutdown.

Risks: The fixed name can collide if multiple on-demand scanners are created in one metrics system without unregistering. It exposes no byte-rate metric even though on-demand scans use a throttler.

Test signals: Registration/unregistration, inherited scanned/unhealthy/iteration counters, duplicate creation behavior, and scanner shutdown cleanup.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/ozoneimpl/OnDemandScannerMetrics.java -->
