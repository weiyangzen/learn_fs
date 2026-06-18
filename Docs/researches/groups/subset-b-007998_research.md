# subset-b-007998 Research

Grouped research for Apache Ozone key-value container handler, packing, helper, block-manager, buffer, dispatcher, dummy, factory, and file-layout strategy classes. Each section preserves its original source path and is delimited for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueHandler.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueHandler.java

## Purpose
`KeyValueHandler` is the datanode request orchestrator for key-value containers. It dispatches container protocol commands, enforces container state and EC replica-index checks, coordinates `BlockManager` and `ChunkManager` operations, handles container lifecycle transitions, exposes import/export/copy/delete hooks, maintains checksum metadata, and performs closed-container reconciliation from peer datanodes.

## Important APIs, Types, And Functions
The class extends `Handler` and owns a `BlockManagerImpl`, a `ChunkManager` from `ChunkManagerFactory`, a `VolumeChoosingPolicy`, a `ContainerChecksumTreeManager`, a striped creation lock set, read/checksum configuration, metrics, and a `BlockInputStreamFactoryImpl`. Main RPC handlers include `dispatchRequest`, `handleCreateContainer`, `handleReadContainer`, `handleUpdateContainer`, `handleDeleteContainer`, `handleCloseContainer`, `handlePutBlock`, `handleFinalizeBlock`, `handleGetContainerChecksumInfo`, `handleGetBlock`, `handleGetCommittedBlockLength`, `handleListBlock`, `handleReadChunk`, `handleWriteChunk`, `handlePutSmallFile`, `handleGetSmallFile`, and `handleStreamInit`. Non-RPC lifecycle APIs include `markContainerForClose`, `quasiCloseContainer`, `closeContainer`, `markContainerUnhealthy`, `updateContainerChecksum`, `importContainer`, `exportContainer`, `copyContainer`, `deleteContainer`, `deleteBlock`, `deleteUnreferenced`, `readBlock`, `addFinalizedBlock`, `isFinalizedBlockExist`, and `reconcileContainer`.

## Control Flow
`handle` delegates to `dispatchRequest`, which validates the request datanode UUID for EC replicas and switches on `ContainerProtos.Type`. Create requests build `KeyValueContainerData`, choose the configured layout, serialize creation with a per-container striped lock, create directories/DB through `KeyValueContainer`, add the container to `ContainerSet`, and send an ICR. Write paths first call `checkContainerOpen`, convert protobuf chunk/block structures to internal objects, optionally validate chunk checksums, delegate chunk writes to the selected layout strategy, then commit block metadata through `BlockManager`. `WriteChunk` can piggyback a put-block during commit stage, while `PutSmallFile` writes one chunk and commits its block in a single flow.

Read paths verify BCSID and EC replica index, call `BlockManager` or `ChunkManager`, adapt old read-chunk versions to single-buffer responses, and update metrics. Close paths move OPEN/RECOVERING to CLOSING, then CLOSING/QUASI_CLOSED to CLOSED, updating checksum metadata from RocksDB when necessary and sending ICRs. Delete acquires a write-locked container from `ContainerSet`, rejects non-force deletion of open or non-empty containers, removes the container from the set, removes DB metadata or cached DB handles, moves the directory to the deleted-container area, then deletes it outside the lock.

Reconciliation reads local and peer container checksum trees, diffs missing/corrupt chunks and deleted blocks, reads peer chunks through `BlockInputStream`, writes repaired chunks to a closed container with overwrite metadata, commits updated block metadata only when possible, updates the Merkle tree after each peer, triggers an on-demand scan, and sends an ICR.

## State And Persistence
Persistent state spans container directories, chunk/block files, `container.yaml`, RocksDB metadata tables, schema-v3 per-volume DB records, finalized-block tables, and checksum tree files. In-memory state includes container lifecycle state, pending put-block cache entries, finalized block local IDs, block/byte statistics, data checksum, and handler-level file/chunk manager caches. `updateAndGetContainerChecksum` persists the data checksum to RocksDB metadata as a startup aid, while the checksum tree file is the authoritative peer-comparison artifact. Delete and import/export flows move or pack whole container directories and metadata, so correctness depends on filesystem atomicity, DB cache cleanup, and ICR timing.

## Dependencies And Integration Points
This class integrates `ContainerSet`, `VolumeSet`, `ContainerMetrics`, `IncrementalReportSender`, `KeyValueContainer`, `BlockUtils`, `ChunkUtils`, `KeyValueContainerUtil`, `BlockManagerImpl`, `ChunkManagerFactory`, Ratis `DispatcherContext`, SCM protocol response builders, Ozone checksum/Merkle tree classes, `DNContainerOperationClient`, `BlockInputStream`, `ChunkInputStream`, security tokens, layout versions, and datanode upgrade gates. It is the central bridge between protobuf container commands and lower-level block/chunk/storage implementations.

## Risks And Test Signals
High-risk areas are state gating around CLOSING/RECOVERING/CLOSED containers, delete locking and force-delete semantics, BCSID idempotency after Ratis replay, chunk checksum validation only on selected paths, cleanup after partial import/export/reconciliation, and reconciliation around holes in block files. Test signals should include command dispatch for all supported RPC types, idempotent create/close/delete replays, WriteChunk staged and combined modes, small-file put/get, FILE_PER_BLOCK readBlock streaming with checksum alignment, closed-container repair of missing/corrupt chunks, checksum file fallback to metadata-built trees, EC replica-index rejection, volume-failure delete paths, and metrics/ICR emission after lifecycle changes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/KeyValueHandler.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/PendingDelete.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/PendingDelete.java

## Purpose
`PendingDelete` is a small immutable value object that carries pending block-deletion count and pending deletion byte totals for key-value container metadata reporting and startup reconciliation.

## Important APIs, Types, And Functions
The class exposes constants `COUNT` and `BYTES`, fields `count` and `bytes`, constructor `PendingDelete(long count, long bytes)`, package-private `addToJson(ObjectNode json)`, and getters `getCount()` and `getBytes()`. `KeyValueContainerUtil` uses instances returned from pending-delete metadata calculation to update container statistics.

## Control Flow
Callers instantiate it after reading metadata-table keys or recalculating pending deletes from delete transaction tables. `addToJson` writes `pendingDeleteBlocks` and `pendingDeleteBytes` into a Jackson `ObjectNode`, preserving field names expected by container metadata inspection/reporting.

## State And Persistence
The object itself is in-memory and immutable. It reflects persisted metadata values from RocksDB tables or derived values from delete transaction tables, but it does not write RocksDB directly.

## Dependencies And Integration Points
It depends only on Jackson `ObjectNode`. It integrates with `KeyValueContainerMetadataInspector` and `KeyValueContainerUtil` through shared field names and values used in `ContainerData` statistics.

## Risks And Test Signals
Risk is low, but field-name drift would break JSON consumers and metadata inspectors. Tests should cover JSON emission, zero-byte pre-storage-space-distribution cases, and startup metadata population using both stored and recalculated pending-delete values.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/PendingDelete.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/TarContainerPacker.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/TarContainerPacker.java

## Purpose
`TarContainerPacker` implements `ContainerPacker<KeyValueContainerData>` for container copy/import/export. It serializes a key-value container into a compressed tar stream containing `container.yaml`, optional checksum tree files, DB metadata dumps or DB files, and chunk files, and it unpacks the same layout into a temporary directory before atomically installing it.

## Important APIs, Types, And Functions
Public methods are `pack`, `unpackContainerData`, `unpackContainerDescriptor`, and static path helpers `getDbPath(KeyValueContainerData)`, `getDbPath(Path, KeyValueContainerData)`, and `getChunkPath(Path)`. Internals include `innerUnpack`, `getContainerMetadataPath`, `getTempContainerMetadataPath`, `compress`, and `decompress`. Constants define archive names: `chunks`, `db`, and `container.yaml`.

## Control Flow
Packing wraps the output stream through `CopyContainerCompression`, opens a tar archive, adds the container descriptor, optionally includes the container checksum file, includes schema-appropriate DB data under `db`, and includes the chunks directory under `chunks`. `unpackContainerData` removes any stale temp unpack directory, computes destination paths inside the temp tree, calls `innerUnpack`, verifies descriptor checksum if present, writes the container descriptor in RECOVERING state into the temp metadata path, and atomically moves the completed temp tree to the destination if the destination is empty. `unpackContainerDescriptor` scans only for `container.yaml` and fails if missing.

## State And Persistence
The class writes and moves real container directories. It preserves chunk and DB contents from the archive, places checksum files under metadata, and intentionally changes the descriptor state to RECOVERING before installation. For schema v3, DB content maps to `DatanodeStoreSchemaThreeImpl.getDumpDir`; for older schemas it maps to the per-container DB path. The destination install uses `StandardCopyOption.ATOMIC_MOVE` and `REPLACE_EXISTING` after checking emptiness.

## Dependencies And Integration Points
It relies on `Archiver` tar helpers, Apache Commons Compress/IO, `ContainerDataYaml`, `ContainerUtils.verifyContainerFileChecksum`, `ContainerChecksumTreeManager`, `KeyValueContainerLocationUtil`, schema-v3 DB dump utilities, `CopyContainerCompression`, and `KeyValueContainer.persistCustomContainerState`. It is invoked by `KeyValueHandler.importContainer` and `exportContainer` through `KeyValueContainer`.

## Risks And Test Signals
Risks include accepting unexpected archive paths only through `extractEntry` path checks, descriptor missing or checksum mismatch, non-empty destination races, schema-v3 dump path mismatches, and partial temp directory cleanup after failures. Tests should cover pack/unpack round trips for schema v1/v2/v3, descriptor-only extraction, checksum file inclusion, unknown tar entry rejection, RECOVERING state persistence, atomic move behavior, and import into an already-existing destination.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/TarContainerPacker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/BlockUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/BlockUtils.java

## Purpose
`BlockUtils` centralizes DB-handle creation/cache management, block-data parsing, BCSID/replica validation, and schema-v3 metadata import/export helpers for key-value containers.

## Important APIs, Types, And Functions
Important methods are `getUncachedDatanodeStore`, `getDB`, `removeDB`, `shutdownCache`, `addDB`, `getBlockData`, `verifyBCSId`, `verifyReplicaIdx`, `removeContainerFromDB`, `dumpKVContainerDataToFiles`, `loadKVContainerDataFromFiles`, and `deleteAllDumpFiles`. It selects `DatanodeStoreSchemaOneImpl`, `DatanodeStoreSchemaTwoImpl`, or `DatanodeStoreSchemaThreeImpl` based on schema version, and chooses `ContainerCache` for schema v1/v2 versus `DatanodeStoreCache` for schema v3.

## Control Flow
`getDB` validates container data and DB file, then opens or retrieves the cached DB handle from the schema-specific cache. IO failures mark the volume failed and are translated to `UNABLE_TO_READ_METADATA_DB`. Add/remove cache operations mirror the same schema split. Metadata export for schema v3 deletes prior dump files, creates the dump directory, calls `dumpKVContainerData`, and cleans partial dumps on failure. Metadata import loads from dump files, removes partially loaded DB state on failure, and deletes dump files in `finally`.

## State And Persistence
DB handles are cached and reference counted outside this utility. Schema v3 container metadata is persisted inside a per-volume DB, while older schemas use per-container DB files. Dump/load helpers materialize schema-v3 KV metadata into external files under the container metadata dump directory for tar replication and then clean them up.

## Dependencies And Integration Points
The class integrates `KeyValueContainerData`, `ContainerCache`, `DatanodeStoreCache`, `ReferenceCountedDB`, `RawDB`, datanode store schema implementations, `StorageVolumeUtil.onFailure`, `BlockData`, protobuf `ContainerProtos`, and error codes such as `UNKNOWN_BCSID`, `CONTAINER_NOT_FOUND`, and metadata import/export failures. It is used by `BlockManagerImpl`, `KeyValueContainerUtil`, `KeyValueHandler`, and block-deletion/startup code.

## Risks And Test Signals
Risks include cache/schema mismatch, leaked DB handles, opening uncached RocksDB while cached handles exist, volume failure escalation on transient DB errors, schema-v3 dump cleanup deleting needed files, and replica-index comparison behavior for EC containers. Tests should cover DB selection by schema, cache add/remove/shutdown, parse malformed block bytes, BCSID ahead-of-container rejection, replica index mismatches, schema-v3 dump/load rollback, and IO-failure result-code translation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/BlockUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/ChunkUtils.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/ChunkUtils.java

## Purpose
`ChunkUtils` provides low-level chunk file IO primitives, validation, locking, mmap/Netty read paths, overwrite detection, size checks, and exception translation for key-value chunk managers.

## Important APIs, Types, And Functions
Key methods include `writeData(File, ChunkBuffer, ...)`, `writeData(FileChannel, ...)`, `readData` overloads for heap/direct buffers, mmap, and Netty `ChunkedNioFile`, `validateChunkForOverwrite`, `isOverWriteRequested`, `verifyChunkFileExists`, `validateBufferSize`, `limitReadSize`, `wrapInStorageContainerException`, and `validateChunkSize`. Static configuration includes `WRITE_OPTIONS`, `READ_OPTIONS`, `DEFAULT_FILE_LOCK_STRIPED_SIZE`, and a test-replaceable `Striped<ReadWriteLock>`.

## Control Flow
Write calls validate buffer length, acquire a per-path write lock when opening by `File`, position the channel, write `ChunkBuffer` data, optionally force-close with fsync, update volume IO statistics, and verify expected byte count. Read calls acquire a per-path read lock, open the file, run a supplied read method, update volume IO stats, and validate read length. Large reads can allocate mmap buffers through `MappedBufferManager` quotas or fall back to normal buffers; Netty reads wrap pooled `ByteBuf`s and register a release callback on `DispatcherContext`. Overwrite helpers detect whether chunk offsets fall within existing file length and only warn if explicit overwrite metadata is absent.

## State And Persistence
The class writes chunk bytes to disk and can fsync file data/metadata. It updates per-volume IO counters but does not update logical container bytes; chunk managers do that after deciding whether writes are commits or overwrites. Mapped read state is held in `MappedBufferManager`, while lock striping is static process state keyed by file path.

## Dependencies And Integration Points
Dependencies include `ChunkBuffer`, `ChunkBufferToByteString`, `BufferUtils`, `ChunkInfo`, `DispatcherContext`, `HddsVolume`, `MappedBufferManager`, Ratis locks/functions, Netty pooled buffers, Java NIO channels, and Ozone/ContainerProtos result codes. It is called by `FilePerBlockStrategy`, `FilePerChunkStrategy`, `ChunkManagerDummyImpl`, and `KeyValueHandler` checksum wrapping.

## Risks And Test Signals
Risks include partial read/write size mismatches, mmap quota leaks if mapped-buffer creation fails, pooled Netty buffer release correctness, false overwrite warnings during replay, lock striping collisions under concurrent IO, and exception translation that hides root detail behind container result codes. Tests should exercise concurrent reads/writes to the same path, fsync and non-fsync writes, zero-length reads, oversized read rejection, file-not-found mapping to `UNABLE_TO_FIND_CHUNK`, overwrite metadata warnings, block-file offset validation, mmap fallback, and Netty release callbacks.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/ChunkUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerLocationUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerLocationUtil.java

## Purpose
`KeyValueContainerLocationUtil` computes canonical filesystem locations for key-value container base directories, metadata directories, chunks directories, and DB files.

## Important APIs, Types, And Functions
Public methods are `getContainerMetaDataPath(String hddsVolumeDir, String clusterId, long containerId)`, `getContainerMetaDataPath(String containerBaseDir)`, `getChunksLocationPath(String baseDir, String clusterId, long containerId)`, `getChunksLocationPath(String containerBaseDir)`, `getBaseContainerLocation`, and `getContainerDBFile`. Private `getContainerSubDirectory` shards containers using `(containerId >> 9) & 0xFF` and `Storage.CONTAINER_DIR`.

## Control Flow
Callers provide either volume/cluster/container identifiers or an already computed container base directory. The utility assembles paths under `<hddsVolumeDir>/<clusterId>/current/<containerSubDirectory>/<containerId>`, then appends metadata or chunks directory names. `getContainerDBFile` returns the per-volume DB for schema v3 using `volume.getDbParentDir()` and `CONTAINER_DB_NAME`; for older schemas it returns `<metadataPath>/<containerId>.db`.

## State And Persistence
The class does not create files. It defines the persistent path contract used by container creation, startup loading, tar packing, deletion, and DB cache lookup.

## Dependencies And Integration Points
It depends on `OzoneConsts`, `Storage`, `KeyValueContainerData`, Guava `Preconditions`, and volume DB-parent configuration. It is consumed by `KeyValueContainer`, `KeyValueContainerUtil`, `TarContainerPacker`, and helpers that need schema-aware DB paths.

## Risks And Test Signals
Risks include path contract drift, negative container IDs, null volume DB parent for schema v3, and sharding mismatch with existing on-disk layouts. Tests should check generated base/meta/chunks paths across container IDs, schema-v3 DB path selection, old-schema DB naming, and null/negative input validation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerLocationUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerUtil.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerUtil.java

## Purpose
`KeyValueContainerUtil` handles creation, loading, statistics reconstruction, checksum loading, emptiness detection, DB removal, and deleted-directory staging for key-value containers.

## Important APIs, Types, And Functions
Key methods are `createContainerMetaData`, `removeContainer`, `removeContainerDB`, `noBlocksInContainer`, `parseKVContainerData`, `getBlockLengthTryCatch`, `getBlockLength`, `isSameSchemaVersion`, `moveToDeletedContainerDir`, and `getTmpDirectoryPath`. Internal helpers include `populateContainerMetadata`, `populatePendingDeletionMetadata`, pre/post storage-space-distribution pending-delete handlers, `populateBlockStatistics`, `populateContainerFinalizeBlock`, `getUsedBytesAndBlockCount`, and `loadAndSetContainerDataChecksum`.

## Control Flow
Creation makes metadata and chunks directories, opens a schema v1/v2 store and caches it, or returns immediately for schema v3 per-volume DBs. Startup parsing optionally verifies the container file checksum, normalizes missing schema to v1, locates the DB file, reads datanode configuration for empty-dir checks, opens the DB by schema, and populates in-memory container metadata. Population reads pending delete count/bytes, delete transaction ID, BCSID, block bytes/count, creates a missing chunks directory, marks empty containers, loads data checksum from RocksDB or checksum tree file, runs configured inspectors, and loads finalized-block local IDs.

Removal first removes DB/cache state, then moves the container directory into the volume's deleted-container directory, deleting any stale target from a previous failed delete. Schema v3 DB removal deletes the container record from the per-volume DB; older schemas only remove cached per-container DB handles.

## State And Persistence
This utility writes metadata/chunks directories, creates DB stores for older schemas, updates in-memory statistics from persisted metadata, may write a newly discovered data checksum into RocksDB, removes schema-v3 KV metadata, and moves container directories to deleted staging. It recalculates missing counters from block/delete tables when metadata keys are missing.

## Dependencies And Integration Points
It integrates `BlockUtils`, `DatanodeStore`, schema v1/v2 classes, `ContainerChecksumTreeManager`, `ContainerInspectorUtil`, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.STORAGE_SPACE_DISTRIBUTION`, `PendingDelete`, `KeyValueContainerMetadataInspector.getAggregatePendingDelete`, `HddsVolume`, and datanode configuration. It is used during container creation, datanode startup loading, delete, export/import preparation, and scanner/inspector repair flows.

## Risks And Test Signals
Risks include partial directory creation cleanup, stale or missing metadata counters, startup behavior when DB files are missing, incorrect schema-v3 DB removal handling, checksum load failures being only warnings, and deleted-container staging overwriting previous leftovers. Tests should cover startup reconstruction for complete and incomplete metadata, old containers without schema version, pending-delete recalculation before/after storage-space-distribution finalization, missing chunks dir repair, finalized-block table loading, no-blocks checks with files on disk, and removal/move failure handling.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/KeyValueContainerUtil.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/package-info.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/package-info.java

## Purpose
Documents that `org.apache.hadoop.ozone.container.keyvalue.helpers` contains utility classes for the key-value container type.

## Important APIs, Types, And Functions
This file declares the package and has no executable APIs. The package contains utilities such as `BlockUtils`, `ChunkUtils`, `KeyValueContainerLocationUtil`, and `KeyValueContainerUtil`.

## Control Flow
There is no runtime control flow.

## State And Persistence
There is no state or persistence behavior. It only contributes package-level Javadoc.

## Dependencies And Integration Points
It is consumed by Javadoc/package documentation tooling and by the Java compiler as a package declaration.

## Risks And Test Signals
Risk is limited to package declaration drift. Compile/Javadoc generation is sufficient signal.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/helpers/package-info.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/BlockManagerImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/BlockManagerImpl.java

## Purpose
`BlockManagerImpl` implements block metadata operations for key-value containers: put/commit block, finalize block, get/list/existence checks, committed length reads, and DB cache shutdown.

## Important APIs, Types, And Functions
Public methods include `putBlock`, `putBlockForClosedContainer`, `persistPutBlock`, `finalizeBlock`, `getBlock`, `getCommittedBlockLength`, read-buffer configuration getters, `deleteBlock`, `listBlock`, `blockExists`, and `shutdown`. Internal helpers include `mergeLastChunkForBlockFinalization`, `getBlockByID`, and `isPartialChunkList`. Configured read settings are default read buffer capacity, mapped-buffer threshold/count, and Netty chunked read toggle.

## Control Flow
`persistPutBlock` opens the container DB, rejects stale nonzero BCSIDs as Ratis replays, checks the pending put-block cache and DB to decide whether block count should increment, enforces upgrade finalization before accepting incremental chunk lists, stores block data through `DatanodeStore.putBlockByID`, updates BCSID/bytes/block-count metadata in a batch, commits, updates in-memory BCSID/statistics, and manages the pending put-block cache according to `endOfBlock`. `putBlockForClosedContainer` performs a similar batched write for closed containers and can avoid overwriting BCSID during partial reconciliation. `finalizeBlock` removes pending-cache state, writes a finalize-block table entry, and merges incremental last-chunk metadata by writing an empty incremental block update.

## State And Persistence
Block metadata, BCSID, bytes used, block count, and finalized-block local IDs are persisted in RocksDB tables. In-memory state on `KeyValueContainerData` mirrors committed BCSID and block statistics, while `KeyValueContainer` tracks pending put-block local IDs for incremental commits. `deleteBlock` is intentionally unsupported because deletion is delegated to `BlockDeletingService`.

## Dependencies And Integration Points
Dependencies include `BlockUtils` for DB and BCSID helpers, `KeyValueContainer`, `KeyValueContainerData`, `DatanodeStore` tables/batches, `VersionedDatanodeFeatures`, `HDDSLayoutFeature.HBASE_SUPPORT`, protobuf `BlockData`, and Ozone read-buffer configuration keys. It is called from `KeyValueHandler`, `FilePerChunkStrategy` partial-read offset logic, and reconciliation.

## Risks And Test Signals
Risks include BCSID replay/idempotency mistakes, block-count overcounting across incremental `putBlock` calls, batch atomicity of block and metadata updates, upgrade-gated incremental chunk lists, finalize-block merge semantics, and cached pending-block state after failures. Tests should cover new and existing blocks, stale and increasing BCSIDs, non-end-of-block incremental writes, end-of-block cache removal, closed-container reconciliation writes with and without BCSID overwrite, finalized-block table persistence, list range/prefix filters, and unsupported delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/BlockManagerImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/Buffers.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/Buffers.java

## Purpose
`Buffers` is a package-private helper for streaming writes that retains the last `max` bytes while exposing older retained `ByteBuffer` references as safe to flush. It supports creating put-block metadata from the trailing bytes in `KeyValueStreamDataChannel` workflows.

## Important APIs, Types, And Functions
The class stores a `Deque<ReferenceCountedObject<ByteBuffer>>`, a `max` retention size, and the current `length`. Methods are `offer`, `poll`, `pollAll`, and `cleanUpAll`, with private `isExtra` and `hasExtraBuffer`. `pollAll` wraps all retained buffers into a read-only Netty `ByteBuf` and returns a reference-counted wrapper that releases all source buffers.

## Control Flow
`offer` retains the incoming reference, appends it, increments total length, and returns an iterable whose iterator repeatedly polls head buffers while removing that buffer would still leave at least `max` bytes. `poll` removes the head reference for writing/release. `pollAll` drains every retained buffer into an `Unpooled.wrappedBuffer` view for final metadata/checksum processing. `cleanUpAll` releases everything left in the deque.

## State And Persistence
All state is in-memory reference-counted buffer ownership. The class does not write storage directly, but incorrect retention/release behavior can leak memory or release buffers still needed by streaming write logic.

## Dependencies And Integration Points
It depends on Guava `Preconditions`, Ratis `ReferenceCountedObject` and `RatisHelper`, Netty `ByteBuf`/`Unpooled`, and `KeyValueStreamDataChannel.LOG`. It is integrated with the streaming data channel used by the file-per-block layout.

## Risks And Test Signals
Risks include reference-count leaks, under-retaining buffers before asynchronous writes, releasing buffers too early through `pollAll`, and invariant failures when `max` is larger than total offered data. Tests should cover offer/flush boundaries, exact `max` retention, pollAll release callbacks, cleanup after exceptions, and mixed buffer sizes.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/Buffers.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDispatcher.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDispatcher.java

## Purpose
`ChunkManagerDispatcher` is a layout-aware facade that implements `ChunkManager` and routes every chunk operation to the strategy matching the container's `ContainerLayoutVersion`.

## Important APIs, Types, And Functions
The constructor installs handlers for `FILE_PER_CHUNK` and `FILE_PER_BLOCK`. It implements `writeChunk`, `streamInit`, `getStreamDataChannel`, `finishWriteChunks`, `finalizeWriteChunk`, `readChunk`, `deleteChunk`, `deleteChunks`, and `shutdown`. Private `selectHandler`, `selectVersionHandler`, and `throwUnknownLayoutVersion` perform routing and unsupported-layout errors.

## Control Flow
Each operation calls `selectHandler(container)` and delegates to the version-specific strategy. `readChunk` additionally verifies non-null returned data and updates container read statistics. Shutdown fans out to all strategy instances.

## State And Persistence
The dispatcher owns an in-memory `EnumMap` of strategy instances. It has no direct persistence behavior, but delegated strategies perform filesystem writes/deletes and file-handle cache management.

## Dependencies And Integration Points
It depends on `FilePerChunkStrategy`, `FilePerBlockStrategy`, `ContainerLayoutVersion`, `ChunkManager`, `BlockManager`, Ratis `StateMachine.DataChannel`, and container metrics. It is created by `ChunkManagerFactory` and used by `KeyValueHandler`.

## Risks And Test Signals
Risks are unsupported layout handling, stale assumptions around the deprecated file-per-chunk layout, and missing strategy shutdown. Tests should cover dispatch for each layout, read-stat updates, unsupported-layout result code, stream data channel routing, and shutdown propagation.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDispatcher.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDummyImpl.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDummyImpl.java

## Purpose
`ChunkManagerDummyImpl` is a non-persistent chunk manager for performance/testing modes where user data is intentionally discarded. Writes only validate/account metrics, and reads return zero-filled data from a mapped temporary backing file.

## Important APIs, Types, And Functions
The class implements `ChunkManager` methods `writeChunk`, `readChunk`, `deleteChunk`, and `deleteChunks`. It creates a read-only zero-filled buffer with static `newMappedByteBuffer(int size)` sized to `OZONE_SCM_CHUNK_MAX_SIZE`.

## Control Flow
Construction creates and maps a temporary zero-filled file. `writeChunk` requires a dispatcher context, validates buffer length and increments volume write IO stats during write stages, then updates container write stats during commit stages. `readChunk` duplicates the zero buffer, caps its limit with `ChunkUtils.limitReadSize`, and wraps it as a `ChunkBuffer`. Delete methods are no-ops because no chunk files exist.

## State And Persistence
No container data is persisted. The only file is a temporary zero backing file marked `deleteOnExit`. Container and volume statistics are still updated to mimic IO behavior.

## Dependencies And Integration Points
It depends on Java NIO mapping APIs, `ChunkUtils`, `ContainerData`, `HddsVolume`, `VolumeIOStats`, `ChunkBuffer`, and `DispatcherContext`. It is selected by `ChunkManagerFactory` when persistence is disabled and scanner configuration allows it.

## Risks And Test Signals
Risks include accidental use outside tests/performance environments, scanner incompatibility, read lengths exceeding the mapped max size, and misleading success despite discarded data. Tests should verify factory selection, write-stage and commit-stage accounting, zero-filled read contents, oversize read rejection, and no-op delete behavior.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerDummyImpl.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerFactory.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerFactory.java

## Purpose
`ChunkManagerFactory` chooses the concrete `ChunkManager` implementation according to datanode configuration for sync writes, persistent data, and scanner compatibility.

## Important APIs, Types, And Functions
The only public API is `createChunkManager(ConfigurationSource conf, BlockManager manager, VolumeSet volSet)`. It reads `HDDS_CONTAINER_CHUNK_WRITE_SYNC_KEY`, `HDDS_CONTAINER_PERSISTDATA`, and `ContainerScannerConfiguration.HDDS_CONTAINER_SCRUB_ENABLED`.

## Control Flow
The factory reads the sync-write flag, then reads whether container data should persist. If persistence is disabled while the container scanner is enabled, it logs a warning and forces persistence back on. If persistence remains disabled, it logs a testing-only data-loss warning and returns `ChunkManagerDummyImpl`. Otherwise it returns a `ChunkManagerDispatcher` configured with the sync flag and block manager.

## State And Persistence
The class itself has no state. Its decision determines whether chunks are durably written to disk or discarded by the dummy manager.

## Dependencies And Integration Points
It depends on Ozone/Hdds config keys, `ContainerScannerConfiguration`, `ChunkManagerDummyImpl`, `ChunkManagerDispatcher`, `BlockManager`, and `VolumeSet` even though the current method does not use `volSet` directly. It is invoked from `KeyValueHandler` construction.

## Risks And Test Signals
Risks include dangerous non-persistent mode, scanner configuration unexpectedly overriding tests, and sync-write flag propagation. Tests should cover persistent/default selection, non-persistent with scanner disabled, non-persistent with scanner enabled forcing dispatcher, and log/config expectations.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/ChunkManagerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerBlockStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerBlockStrategy.java

## Purpose
`FilePerBlockStrategy` implements `ChunkManager` for the FILE_PER_BLOCK layout, where all chunks of a block are stored in one block file. It handles streaming initialization, staged/final writes, reads, deletes, overwrite accounting, and open file-channel caching.

## Important APIs, Types, And Functions
Main methods are `streamInit`, `getStreamDataChannel`, `writeChunk`, `readChunk`, `deleteChunk`, `deleteChunks`, `finishWriteChunks`, `finalizeWriteChunk`, and private `deleteChunk`, `getChunkFile`, and `checkFullDelete`. The nested `OpenFiles` cache maps file paths to `OpenFile` instances with 10-minute expire-after-access and removal-triggered close. Constructor configuration pulls read buffer capacity, mmap thresholds, max mapped buffer count, and Netty read toggle from `BlockManager`.

## Control Flow
`writeChunk` verifies the container uses FILE_PER_BLOCK, skips empty chunks and COMMIT_DATA-only calls, gets or opens the block file channel, detects overwrite, validates append offsets for non-overwrites, records file length, writes data at the chunk offset, accounts only the growth delta for overwrites extending the file, and updates container write stats. `readChunk` validates length, chooses buffer capacity, and reads from the block file with Netty, mmap, or normal buffers. `finishWriteChunks` and `finalizeWriteChunk` close cached file handles and verify the block file exists. Deletion removes the entire block file; single-chunk delete is allowed only when the requested range covers the whole file.

## State And Persistence
This strategy persists block files under the container chunks directory using layout-derived names. The open-file cache keeps `RandomAccessFile` channels live and invalidates them on finish/finalize. Container statistics and volume used-space accounting are updated based on new writes or overwrite growth. Delete physically removes block files but leaves block metadata cleanup to the caller.

## Dependencies And Integration Points
Dependencies include `ChunkUtils`, `ContainerLayoutVersion.FILE_PER_BLOCK`, `KeyValueStreamDataChannel`, `MappedBufferManager`, `BlockManager` read settings, `ContainerMetrics`, Hadoop `FileUtil`, Guava cache, Ratis `StateMachine.DataChannel`, and Ozone container/chunk abstractions. It is selected by `ChunkManagerDispatcher` and used heavily by `KeyValueHandler`, including closed-container reconciliation.

## Risks And Test Signals
Risks include cached file channel staleness after external replacement, offset/file-length inconsistency, overwrite accounting errors, partial delete rejection, force/sync mode behavior, and mapped-buffer resource limits. Tests should cover append writes, pure overwrites, overwrites that extend files, COMMIT_DATA no-op, stream data channel writes, finish/finalize closing handles, full and partial delete behavior, reads through normal/mmap/Netty paths, and volume failure handling on IO exceptions.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerBlockStrategy.java -->

<!-- BEGIN_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerChunkStrategy.java -->
# sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerChunkStrategy.java

## Purpose
`FilePerChunkStrategy` implements `ChunkManager` for the FILE_PER_CHUNK layout, where each chunk is a separate file. It supports Ratis write/commit staging through temporary chunk files, combined writes, reads with temporary-file fallback, and per-chunk deletion.

## Important APIs, Types, And Functions
Main methods are `writeChunk`, `readChunk`, `deleteChunk`, `deleteChunks`, private `getChunkFile`, `getTmpChunkFile`, and `commitChunk`. Constructor state includes sync-write flag, `BlockManager`, read buffer/mmap settings, `MappedBufferManager`, and Netty read toggle.

## Control Flow
`writeChunk` verifies FILE_PER_CHUNK layout, derives the final and temporary chunk files, detects overwrites, then switches on dispatcher stage. `WRITE_DATA` deletes an existing final file during retry-like overwrite scenarios, warns if a temp file already exists, and writes payload to the temp file without updating committed stats. `COMMIT_DATA` returns idempotently if the final file already exists, otherwise renames the temp file to final and updates stats. `COMBINED` writes directly to final and updates stats. `readChunk` builds possible final/temp/final candidates when the dispatcher says reads may come from temp files, resolves chunk-file offset through `BlockManager` when the requested chunk offset is nonzero, and reads through Netty, mmap, or normal buffers. Delete permits removing a chunk file only when metadata length matches the file size or offset+length matches legacy shared-file expectations.

## State And Persistence
The strategy persists one file per chunk plus temporary files named with term and log index. Stats are updated on commit/combined writes, not initial staged writes. It does not update block metadata; `BlockManager` commits metadata separately. Deletion physically removes chunk files.

## Dependencies And Integration Points
Dependencies include `ChunkUtils`, `ContainerLayoutVersion.FILE_PER_CHUNK`, `BlockManager` for offset resolution and read settings, `DispatcherContext`, `OzoneConsts` temporary chunk naming, Hadoop `FileUtil`, and container/chunk abstractions. Although `KeyValueHandler` warns that FILE_PER_CHUNK is not supported as configured layout, this strategy remains available for older containers/tests through the dispatcher.

## Risks And Test Signals
Risks include temp-file leftovers after Ratis truncation, final-file idempotency masking checksum mismatches, offset handling for partial reads, unsupported shared-file delete cases, and deprecated layout coverage gaps. Tests should cover staged write/commit, replay of existing final chunks, temp-file read fallback race, combined writes, nonzero-offset reads via block metadata, delete length validation, missing chunk errors, and mmap/Netty read variants.
<!-- END_FILE_RESEARCH: sources/object-store/apache-ozone/hadoop-hdds/container-service/src/main/java/org/apache/hadoop/ozone/container/keyvalue/impl/FilePerChunkStrategy.java -->
