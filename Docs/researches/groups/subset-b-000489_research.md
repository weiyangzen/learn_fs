# Research Report: subset-b-000489

Grouped research for Alluxio worker block metadata, local/UFS block storage, master synchronization, cache loading, registration streaming, and allocation policy files. Each section preserves the source path in its title and is wrapped for reconciliation splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataEvictorView.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataEvictorView.java

### Purpose
`BlockMetadataEvictorView` is a narrowed, non-thread-safe view over `BlockMetadataManager` for eviction and allocation decisions. It materializes tier and directory views while filtering block metadata access through evictability rules so eviction logic does not need to understand pinned inodes, locked blocks, or blocks already marked for movement in the current view.

### Important APIs and Types
- `BlockMetadataEvictorView(BlockMetadataManager, Set<Long> pinnedInodes, Set<Long> lockedBlocks)` snapshots pinned file ids and locked block ids.
- `initializeView()` wraps each `StorageTier` as a `StorageTierEvictorView`.
- `getDirs(BlockStoreLocation)` returns all directory views whose locations belong to the requested tier/dir/medium wildcard.
- `clearBlockMarks()` clears per-directory move-in/move-out markings.
- `isBlockPinned`, `isBlockLocked`, `isBlockMarked`, and `isBlockEvictable` compose the filtering rules.
- `getBlockMeta(long)` returns metadata only when the block is currently evictable.

### Control Flow
Construction delegates to `BlockMetadataView`, which immediately calls `initializeView`; after that the constructor fills pinned and locked sets. This ordering is acceptable because `initializeView` only builds wrapper objects and does not use the filter sets. Evictors call `getDirs` to scope candidates, use `isBlockEvictable` to guard deletion, and use `getBlockMeta` to avoid accidentally exposing protected blocks.

### State and Persistence
The class holds in-memory snapshots of pinned inodes and locked blocks and in-memory tier/dir views. It persists nothing directly. Physical block deletion and metadata mutation happen later through `TieredBlockStore` and `BlockMetadataManager`.

### Dependencies and Integration Points
It depends on `BlockId.getFileId` to map block ids to file ids, metadata wrappers in `alluxio.worker.block.meta`, and the underlying `BlockMetadataManager` for live capacity and block metadata. `TieredBlockStore.getUpdatedView` creates this view during free-space eviction, and allocators may receive it at construction time.

### Risks
- The class is explicitly not thread-safe; callers must build and use it under higher-level metadata/eviction synchronization.
- It snapshots pinned and locked state. Long-lived instances can become stale, which is why `TieredBlockStore` rebuilds it before freeing space.
- The TODO notes unallocatable space is not yet filtered, so allocator/evictor consumers still rely on later allocation checks.

### Test Signals
`BlockMetadataViewTest` exercises tier lookup, tier-below behavior, available bytes, `getBlockMeta`, and pinned/locked filtering. Eviction behavior is indirectly tested by `TieredBlockStore` and allocator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataEvictorView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataManager.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataManager.java

### Purpose
`BlockMetadataManager` is the central non-thread-safe owner of local tiered-storage metadata. It constructs configured storage tiers, locates block and temp block metadata, mutates directory accounting on create/commit/abort/move/remove/resize, and supplies `BlockStoreMeta` snapshots for worker registration and heartbeats.

### Important APIs and Types
- `WORKER_STORAGE_TIER_ASSOC` maps configured worker tier ordinals to aliases.
- `createBlockMetadataManager()` constructs a configured manager.
- `getBlockIterator()` exposes the configured block iteration/annotation provider for eviction and management tasks.
- Temp-block lifecycle: `addTempBlockMeta`, `abortTempBlockMeta`, `commitTempBlockMeta`, `cleanupSessionTempBlocks`, `resizeTempBlockMeta`.
- Lookup and snapshots: `getAvailableBytes`, `getBlockMeta`, `getTempBlockMeta`, `getSessionTempBlocks`, `getBlockStoreMeta`, `getBlockStoreMetaFull`.
- Topology: `getTier`, `getDir`, `getTiers`, `getTiersBelow`, `getStorageTierAssoc`.
- Mutations: `moveBlockMeta` and `removeBlockMeta`.

### Control Flow
The private constructor builds each `DefaultStorageTier` from tier configuration, indexes tiers by alias, then chooses a block iterator. Deprecated evictor class settings are translated to `LRUAnnotator` or `LRFUAnnotator`; custom legacy evictors are wrapped by `EmulatingBlockIterator`; otherwise `DefaultBlockIterator` is used. Commit converts a `TempBlockMeta` into `DefaultBlockMeta`, removes it from the temp map, and adds it to the committed block map in the same `StorageDir`. Move removes the source block metadata, removes the destination temp placeholder, and creates a new committed metadata entry in the destination dir.

### State and Persistence
State is in-memory metadata for configured tiers and directories. The underlying `StorageDir` implementations reflect worker storage directories and block files, but this class itself only maintains metadata accounting. It must be guarded by `TieredBlockStore` metadata locks for thread safety.

### Dependencies and Integration Points
It integrates with `TieredBlockStore` for all local metadata operations, `DefaultBlockStoreMeta` for snapshots, block annotators/iterators for eviction order, allocators/evictors through `BlockMetadataView`, and configuration keys for tier layout and deprecated eviction behavior.

### Risks
- Linear scans over all tiers/dirs for block lookup and existence checks can be expensive with many directories or blocks.
- The constructor mutates global configuration when translating deprecated evictors, which can surprise later components.
- `moveBlockMeta` assumes physical file movement has already succeeded; rollback is handled by the caller, and `TieredBlockStore` currently documents limited rollback.
- No internal locking; accidental direct concurrent use would corrupt metadata/accounting.

### Test Signals
`BlockMetadataManagerTest` covers tier/dir lookup, available bytes, missing tier errors, block/temp lookup, moving metadata, and resizing temp blocks. Management-tier tests use it through `TieredBlockStoreTestUtils`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataView.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataView.java

### Purpose
`BlockMetadataView` is the abstract base for read-only-ish metadata projections consumed by allocators and evictors. It builds and refreshes tier view objects from a `BlockMetadataManager` while preserving tier ordering and tier alias lookup.

### Important APIs and Types
- Constructors accept a `BlockMetadataManager` and optional `useReservedSpace` flag.
- `getTierView(String)` validates and returns a `StorageTierView`.
- `getTierViews()` exposes an unmodifiable ordered list.
- `getNextTier(StorageTierView)` and `getTierViewsBelow(String)` support tier traversal.
- `initializeView()` is implemented by concrete views.
- `refreshView()` clears and rebuilds the projection in-place.

### Control Flow
Construction stores the manager and reserved-space flag, then calls subclass `initializeView`. Consumers can refresh the same view object after metadata changes; refresh clears tier lists and alias maps before reinitializing them.

### State and Persistence
State is an in-memory list/map of `StorageTierView` wrappers. It persists nothing and makes no metadata mutations. The reserved-space flag is consumed by concrete dir/tier views that calculate available bytes.

### Dependencies and Integration Points
Subclasses include `BlockMetadataEvictorView` and `BlockMetadataAllocatorView`. Allocators use this API to reason about capacity without directly touching `StorageTier` internals.

### Risks
- The constructor invokes an abstract method, so subclass initialization must not depend on subclass fields that are assigned after `super(...)`.
- It is not synchronized and assumes its backing metadata manager is guarded externally.
- `getTierViewsBelow` returns a `subList` view, so callers should not assume independent snapshot semantics.

### Test Signals
`BlockMetadataViewTest` validates alias lookup, tier lists, below-tier behavior, refresh-compatible comparisons with manager tiers, and exception paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetadataView.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetricsReporter.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetricsReporter.java

### Purpose
`BlockMetricsReporter` is a thread-safe block-store event listener that translates local block events into worker metrics counters and an eviction-rate meter.

### Important APIs and Types
- Extends `AbstractBlockStoreEventListener`.
- Overrides `onAccessBlock`, `onMoveBlockByClient`, `onRemoveBlockByClient`, `onMoveBlockByWorker`, `onRemoveBlockByWorker`, `onAbortBlock`, and `onBlockLost`.
- Uses static `MetricsSystem.counter` and `meterWithTags` registrations for worker block metrics.

### Control Flow
Event callbacks increment counters. Move callbacks compare old/new tier ordinals and increment promoted-block count when a block moves to tier ordinal 0 from another tier. Worker removals increment both evicted-block counter and eviction-rate meter; client removals increment deleted-block counter.

### State and Persistence
Only metrics are mutated. There is no durable state and no block metadata mutation.

### Dependencies and Integration Points
`DefaultBlockWorker` registers this listener with the block store. It relies on `BlockMetadataManager.WORKER_STORAGE_TIER_ASSOC` to interpret promotion.

### Risks
- Promotion semantics are hard-coded to tier ordinal 0.
- Static metric objects are process-wide; tests must reset metrics if they assert counts.

### Test Signals
`BlockWorkerMetricsTest` covers worker metrics gauges. Event counter behavior is indirectly exercised by block-store tests that register listeners and by metric integration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockMetricsReporter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockSyncMasterGroup.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockSyncMasterGroup.java

### Purpose
`BlockSyncMasterGroup` manages per-master block synchronization when a worker registers to all masters. It creates one `SpecificMasterBlockSync` per configured master, registers each heartbeat reporter with the block store, starts heartbeat threads, and exposes registration-state checks.

### Important APIs and Types
- Constructor accepts master addresses and a `BlockWorker`.
- `start(ExecutorService)` submits heartbeat threads for each sync operator.
- `waitForPrimaryMasterRegistrationComplete(InetSocketAddress)` blocks until the primary sync is registered or fatally exits on timeout.
- `isRegisteredToAllMasters()` and `getMasterSyncOperators()` expose state.
- Nested `Factory.createAllMasterSync` obtains configured master RPC addresses.
- Nested `BlockMasterClientFactory` is test-injectable.

### Control Flow
For every master address, the constructor creates a `BlockMasterClient`, a new `BlockHeartbeatReporter`, registers that reporter as a block-store listener, and creates either `SpecificMasterBlockSync` or `TestSpecificMasterBlockSync` depending on test mode. `start` submits each sync to a `HeartbeatThread` with the worker block heartbeat interval.

### State and Persistence
State is an in-memory map of master address to sync operator and a volatile started flag. It persists nothing. Registration/heartbeat state lives in each `SpecificMasterBlockSync`.

### Dependencies and Integration Points
Used by all-master-registration worker mode. It integrates with `ConfigurationUtils`, `HeartbeatThread`, `BlockMasterClient`, `BlockWorker.getBlockStore`, and the `SpecificMasterBlockSync` implementation.

### Risks
- Master membership changes are explicitly TODO; the map is fixed at construction.
- `start` sets `mStarted` but still submits heartbeat threads on repeated calls after the first, since the submit loop is outside the guard.
- A heartbeat reporter is registered per master, so event fanout and memory grow with master count.

### Test Signals
`AllMasterRegistrationBlockWorkerTest` uses the test client factory and test syncs. `SpecificMasterBlockSyncTest` covers sync behavior below this grouping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockSyncMasterGroup.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockWorkerFactory.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockWorkerFactory.java

### Purpose
`BlockWorkerFactory` creates and registers the concrete block worker for the process. It selects page-store or file-store implementation and wraps it in either default single-primary registration or all-master registration worker mode.

### Important APIs and Types
- Implements `WorkerFactory`.
- `isEnabled()` always returns true.
- `create(WorkerRegistry, UfsManager)` builds `BlockMasterClientPool`, shared worker id reference, block store, file-system master client, worker, and registry entry.

### Control Flow
Factory reads `WORKER_BLOCK_STORE_TYPE`. `PAGE` creates `PagedBlockStore`; `FILE` creates `MonoBlockStore(new TieredBlockStore(), ...)`. It then reads `WORKER_REGISTER_TO_ALL_MASTERS` captured in a field and creates `AllMasterRegistrationBlockWorker` or `DefaultBlockWorker`, registers it under `BlockWorker.class`, and returns it.

### State and Persistence
The factory itself holds only one config-derived boolean. Created workers own runtime state and storage persistence.

### Dependencies and Integration Points
It bridges worker bootstrap (`WorkerRegistry`) with block-store implementations, UFS manager, block master client pool, file-system master client, sessions, and worker id reference.

### Risks
- Unsupported enum values throw `UnsupportedOperationException`, so new block store types require factory edits.
- The all-master config is captured at factory instantiation; late config changes would not be reflected.

### Test Signals
Worker creation paths are covered indirectly by `DefaultBlockWorkerTestBase`, `AllMasterRegistrationBlockWorkerTest`, and page/file store tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/BlockWorkerFactory.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CacheRequestManager.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CacheRequestManager.java

### Purpose
`CacheRequestManager` handles synchronous and asynchronous requests to cache a block on the worker. It deduplicates active requests by block id, chooses local UFS versus remote-worker source, performs the copy/read into the local block store, and records cache metrics.

### Important APIs and Types
- Constructor takes an executor, `DefaultBlockWorker`, and `FileSystemContext`.
- `submitRequest(CacheRequest)` is the public entry point.
- Inner `CacheTask` executes one request and defines equality/hash by block id.
- `CacheResult` distinguishes `SUCCEED`, `FAILED`, and `ALREADY_CACHED`.
- `cacheBlockFromUfs` reads the whole block through UFS fallback reader and commits temp metadata.
- `cacheBlockFromRemoteWorker` creates a temp local block, copies from `RemoteBlockReader` to `BlockWriter`, then commits.
- `getRemoteBlockReader` is visible for testing.

### Control Flow
`submitRequest` increments request metrics, rejects duplicate active block ids, and either returns for async duplicates or waits up to 30 seconds for sync duplicates. New requests are submitted to the cache executor. Sync callers wait on the future and receive translated exceptions. The task removes its block id from `mActiveCacheRequests` in `finally` and increments success/failure/size counters. Source selection compares `sourceHost` to local host; local reads go through UFS and remote reads go through a remote block stream.

### State and Persistence
Active requests are tracked in a `ConcurrentHashMap<Long, CacheRequest>`. Persistent effects are local temp/committed block files and metadata created through `DefaultBlockWorker`/`BlockStore`. Failed UFS and remote copies abort matching temp blocks when present.

### Dependencies and Integration Points
The manager is owned by `DefaultBlockWorker` and uses `BlockReader`, `BlockWriter`, `RemoteBlockReader`, `NetworkAddressUtils`, `BufferUtils`, sessions reserved for cache, and worker cache metrics.

### Risks
- Sync duplicate waiting is bounded to 30 seconds and can report cancellation even if the original request later succeeds.
- Remote cache creates a local temp block before opening the remote reader, so failures must reliably abort to avoid leaked temp files.
- UFS cache assumes full-block sequential read; partial reads do not satisfy caching.
- The async executor rejection path is best-effort for async but fatal to sync callers.

### Test Signals
Cache behavior is typically tested through `DefaultBlockWorker` cache tests and by mocking `getRemoteBlockReader`; source references show several worker grpc tests exercising cache/fallback paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CacheRequestManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CachedSeekableInputStream.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CachedSeekableInputStream.java

### Purpose
`CachedSeekableInputStream` wraps a `SeekableUnderFileInputStream` with cache bookkeeping metadata so `UfsInputStreamCache` can associate reusable UFS streams with a resource id, file id, and file path.

### Important APIs and Types
- Package-private constructor takes an existing seekable stream, resource id, file id, and file path.
- `getResourceId`, `getFilePath`, and `getFileId` expose metadata to the cache.

### Control Flow
Construction delegates all stream behavior to the superclass wrapper, validates the resource id is non-negative, and stores identifiers. All actual read/seek/close behavior comes from `SeekableUnderFileInputStream`.

### State and Persistence
State is per-stream metadata only. It does not persist data and does not own cache membership; `UfsInputStreamCache` does.

### Dependencies and Integration Points
Used only by `UfsInputStreamCache` for Guava-cache values and removal bookkeeping.

### Risks
- The validation message says positive but accepts zero (`>= 0`).
- Package-private getters keep use local, but any incorrect file id/resource id assignment can break cache tracking.

### Test Signals
Covered indirectly by `UfsInputStreamCache` use in `UnderFileSystemBlockReaderTest` and UFS read paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/CachedSeekableInputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockStoreMeta.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockStoreMeta.java

### Purpose
`DefaultBlockStoreMeta` is a snapshot implementation of `BlockStoreMeta` built from `BlockMetadataManager`. It reports tier/dir capacity, used bytes, optional block id lists, directory paths, storage tier association, and lost storage.

### Important APIs and Types
- Constructor `DefaultBlockStoreMeta(BlockMetadataManager, boolean shouldIncludeBlockIds)`.
- Capacity/usage getters: `getCapacityBytes`, `getCapacityBytesOnTiers`, `getCapacityBytesOnDirs`, `getUsedBytes`, `getUsedBytesOnTiers`, `getUsedBytesOnDirs`.
- Block lists: `getBlockList`, `getBlockListByStorageLocation`, `getNumberOfBlocks`.
- Topology/loss: `getDirectoryPathsOnTiers`, `getLostStorage`, `getStorageTierAssoc`.

### Control Flow
The constructor walks all tiers and dirs once, accumulating tier totals and dir maps. If full block ids are requested, it also creates tier-level and location-level block id lists. Finally, it copies lost storage paths from tiers into a tier-keyed map.

### State and Persistence
This object is an in-memory snapshot. It does not mutate block metadata or storage files. When `shouldIncludeBlockIds` is false, block-list fields are null and block-list getters enforce non-null via `Preconditions`.

### Dependencies and Integration Points
Created by `BlockMetadataManager.getBlockStoreMeta` and `getBlockStoreMetaFull`; consumed by worker registration, heartbeat metrics gauges, master commit calls, and UI/API metadata responses.

### Risks
- Some returned maps are mutable internal maps, while `getUsedBytesOnTiers` wraps unmodifiable; callers could mutate snapshot fields inconsistently.
- Full metadata snapshots allocate block id lists for every directory and can be expensive/OOM-prone for very large workers.
- Block-list getters throw if called on a non-full snapshot.

### Test Signals
Covered indirectly by `BlockWorkerMetricsTest`, registration tests, and metadata manager/store tests that compare capacity and block lists.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockStoreMeta.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockWorker.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockWorker.java

### Purpose
`DefaultBlockWorker` is the top-level block worker service implementation. It owns block-store access, master clients, heartbeat reporting, session cleanup, pin-list sync, optional storage health checks, optional internal FUSE mount, cache request handling, configuration reporting, metrics registration, and checksum calculation.

### Important APIs and Types
- Constructor wires `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `BlockStore`, worker id reference, event listeners, cache manager, fuse manager, and checksum resources.
- Lifecycle: `start(WorkerNetAddress)`, `setupBlockMasterSync`, `askForWorkerId`, `stop`.
- Block operations: `createBlock`, `createBlockWriter`, `createBlockReader`, `createUfsBlockReader`, `commitBlock`, `abortBlock`, `removeBlock`, `requestSpace`, `commitBlockInUfs`.
- Metadata/reporting: `getReport`, `getStoreMeta`, `getStoreMetaFull`, `getConfiguration`, `getWhiteList`, `updatePinList`, `getFileInfo`.
- Cache/load: deprecated `asyncCache`, `cache(CacheRequest)`, `load(List<Block>, UfsReadOptions)`.
- Admin/metrics: `freeWorker`, `clearMetrics`, nested `Metrics.registerGauges`, nested `StorageChecker`, `calculateBlockChecksum`.

### Control Flow
Startup obtains a worker id from the block master with retry, starts block-master sync, starts pin-list heartbeat, starts session cleaner, optionally starts storage checker and internal FUSE. Most public block APIs delegate to `mBlockStore`, translating resource-exhausted create failures into messages with debug URLs when the worker address is known. `cache` is skipped for `PagedBlockStore`; file store cache is delegated to `CacheRequestManager`. `load` creates temp blocks in the top tier, schedules UFS reads through `UfsIOManager`, appends direct buffers to block writers, commits, and returns accumulated per-block `BlockStatus` errors. Checksum calculation reads blocks in parallel, computes CRC64 in 8 MiB chunks, optionally rate-limits, and returns a map of checksums.

### State and Persistence
Worker state includes master clients, sessions, event reporters, worker id/address, block store, cache manager, FUSE manager, checksum executor, and metric gauges. Persistent effects are through the block store and UFS/master RPCs: block files, metadata, master commit notifications, UFS commit notifications, and storage cleanup in `freeWorker`.

### Dependencies and Integration Points
It sits at the center of worker integration: `BlockMasterSync`, `PinListSync`, `SessionCleaner`, `BlockStore`, `FileSystemMasterClient`, `FileSystemContext`, gRPC executors, `MetricsSystem`, optional `FuseManager`, and client/server block IO handlers.

### Risks
- `Metrics.WORKER_ACTIVE_CLIENTS` is incremented/decremented across several paths; mismatches can occur on exceptional close/abort paths.
- `freeWorker` recursively deletes all entries in configured worker storage dirs and must only be called for administrative cleanup.
- `load` allocates a direct buffer of full block size per block, so large or many blocks can exhaust direct memory despite retry.
- Checksum results are written into a plain `HashMap` from multiple futures, which is not thread-safe.
- `getConfiguration` explicitly does not guarantee a single consistent cluster/path snapshot.

### Test Signals
`DefaultBlockWorkerTestBase`, `DefaultBlockWorkerExceptionTest`, `BlockWorkerMetricsTest`, block grpc handler tests, and stream reader tests cover worker construction, exception handling, metrics, cache/read/write paths, and UFS fallback behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/DefaultBlockWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/FuseManager.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/FuseManager.java

### Purpose
`FuseManager` owns the lifecycle of the worker-internal Alluxio FUSE application when worker FUSE is enabled.

### Important APIs and Types
- Constructor stores `FileSystemContext` and creates a `Closer`.
- `start()` creates a `FileSystem` and launches FUSE with `FuseOptions`.
- `close()` unmounts and closes registered resources.

### Control Flow
`start` registers a `FileSystem` in the resource closer and invokes `AlluxioFuse.launchFuse(..., false)`. Errors are caught broadly and logged so worker startup does not immediately propagate the FUSE launch failure. `close` attempts forced unmount if FUSE was launched, logs unmount errors, then closes the resource closer.

### State and Persistence
Runtime state is the FUSE unmount handle and closeable resources. It does not persist Alluxio block data directly.

### Dependencies and Integration Points
Created by `DefaultBlockWorker` and started only when `WORKER_FUSE_ENABLED` is true. Depends on Alluxio FUSE, file-system client, and worker file-system context.

### Risks
- Launch failures are logged but swallowed, so callers need logs/health checks to detect missing FUSE.
- TODO notes launch can block and may deserve its own thread/status tracking.
- Already-mounted handling is not implemented.

### Test Signals
No direct test surfaced in the searched references; coverage is mostly through worker lifecycle tests when FUSE is disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/FuseManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/LocalBlockStore.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/LocalBlockStore.java

### Purpose
`LocalBlockStore` defines the contract for a local worker block store that owns block/temp-block metadata, local block files, block locks, allocation, movement, removal, access notifications, session cleanup, pin-list updates, and storage health handling.

### Important APIs and Types
- Creation and temp lifecycle: `createBlock`, `createBlockWriter`, `requestSpace`, `commitBlock`, `commitBlockLocked`, `abortBlock`.
- Reading and locking: `pinBlock`, `createBlockReader(session, block, offset)`, default UFS-aware overload.
- Mutation: `moveBlock`, `removeBlock`, `removeInaccessibleStorage`.
- Metadata: `getVolatileBlockMeta`, `getTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, `hasBlockMeta`, `hasTempBlockMeta`.
- Events/session: `accessBlock`, `cleanupSession`, `registerBlockStoreEventListener`, `updatePinnedInodes`.

### Control Flow
This is an interface, but its documentation establishes the expected lifecycle: create temp metadata and temp path; write privately; request additional space as needed; commit to make visible; pin before reading committed blocks; move/remove under appropriate locks; cleanup sessions by unlocking and deleting temp data.

### State and Persistence
Implementations are expected to maintain local metadata and physical block/temp files. The interface extends `SessionCleanable` and `Closeable`.

### Dependencies and Integration Points
`TieredBlockStore` is the main implementation in this subset. `MonoBlockStore` composes it with UFS access, and `DefaultBlockWorker` exposes it through the higher-level `BlockStore` API.

### Risks
- `getVolatileBlockMeta` explicitly returns metadata without a lock guarantee, so callers must handle movement/removal races.
- The default UFS-aware reader throws `UnsupportedOperationException`; only higher layers/implementations that support fallback should call it.
- `commitBlockLocked` transfers lock ownership to the caller, making close discipline essential.

### Test Signals
All local store behavior is exercised through `TieredBlockStore` tests, `UnderFileSystemBlockReaderTest`, `MonoBlockStoreCommitBlockTest`, and grpc block read/write tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/LocalBlockStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/MonoBlockStore.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/MonoBlockStore.java

### Purpose
`MonoBlockStore` implements the higher-level `BlockStore` contract for whole-block storage. It composes a `LocalBlockStore` with `UnderFileSystemBlockStore`, forwards local operations, reports committed blocks to the master, handles local-cache-first reads with UFS fallback, and supports asynchronous bulk UFS loading.

### Important APIs and Types
- Constructor wires local store, block master client pool, UFS manager, and worker id.
- Local delegation: create/write/read/abort/move/remove/requestSpace/metadata/pin/updatePinnedInodes.
- `commitBlock` commits locally under a returned lock, then calls `BlockMasterClient.commitBlock` and notifies listeners.
- `createUfsBlockReader` delegates to `UnderFileSystemBlockStore` and wraps close to close/release UFS access.
- `load(List<Block>, UfsReadOptions)` bulk reads through `UfsIOManager` into local blocks.
- `closeUfsBlock`, `handleException`, and `timeoutAfter` handle UFS lifecycle/load errors.

### Control Flow
Reads first try `mLocalBlockStore.createBlockReader`. If the block is absent and UFS options include a path or UFS-tier flag, it opens a UFS block reader. UFS reader close triggers `closeBlock` and `releaseAccess`; no-cache reads decrement active-client metrics when no temp block exists. Commits acquire a master client, call `commitBlockLocked`, fetch committed local metadata, report used bytes/tier/medium/block size to master, notify listeners, release client, and decrement active clients. Bulk load creates local temp blocks in top tier, reads from UFS into direct buffers with timeout/retry, appends to writers, commits, releases buffers, and records block-level errors.

### State and Persistence
State includes composed local/UFS stores, listener list, block master client pool, worker id, and a scheduled delayer for load timeouts. Persistent effects include local block files, local metadata, master block metadata commits, and UFS read stream lifecycle.

### Dependencies and Integration Points
Used by `BlockWorkerFactory` for file block store mode and by `DefaultBlockWorker`. Integrates with `UnderFileSystemBlockStore`, `UfsIOManager`, `BlockMasterClient`, `BlockStoreEventListener`, `GrpcExecutors`, direct buffer pools, and worker metrics.

### Risks
- Commit notifies master while holding the local block lock returned by `commitBlockLocked`; slow master RPC can prolong block write locking.
- Bulk `load` uses full block-size direct buffers and may stress memory.
- `mBlockStoreEventListeners` is maintained separately while listener registration also forwards to local store; listener ordering and duplicate notification semantics need care.
- `closeUfsBlock` metric decrement depends on temp metadata/no-cache state and can drift if exception paths change.

### Test Signals
`MonoBlockStoreCommitBlockTest` focuses commit/listener/master behavior. `UfsFallbackBlockWriteHandlerTest`, `ShortCircuitBlockReadHandlerTest`, and stream reader tests cover construction and read/write integration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/MonoBlockStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/PinListSync.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/PinListSync.java

### Purpose
`PinListSync` is a heartbeat executor that periodically fetches pinned file ids from the file-system master and updates the block worker’s pin list so eviction avoids pinned file blocks.

### Important APIs and Types
- Constructor takes `BlockWorker` and `FileSystemMasterClient`.
- `heartbeat(long)` calls `getPinList()` and `updatePinList`.
- `close()` is a no-op.

### Control Flow
Each heartbeat requests the current pin list from the master. On success it updates the worker. Exceptions are logged at warn/debug and do not propagate, allowing later heartbeats to retry.

### State and Persistence
No internal mutable state beyond dependencies. The persistent effect is indirect: updated in-memory pin set in the block store, which affects future eviction.

### Dependencies and Integration Points
Started by `DefaultBlockWorker.start` in a heartbeat thread. Feeds `TieredBlockStore.updatePinnedInodes`, which is read by `BlockMetadataEvictorView`.

### Risks
- A failed heartbeat leaves the previous pin list in effect, which can either over-protect old pins or fail to protect new pins until the next successful sync.
- It fetches the complete pin list each time; large pin sets can create memory/serialization pressure.

### Test Signals
`PinListSyncTest` covers successful update and exception-tolerant heartbeat behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/PinListSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RegisterStreamer.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RegisterStreamer.java

### Purpose
`RegisterStreamer` streams worker registration data to the block master as a sequence of `RegisterWorkerPRequest` batches. It packages worker capacity, usage, config, lost storage, build version, and block-location batches while applying simple flow control and response/error handling.

### Important APIs and Types
- Multiple constructors accept async gRPC stub, worker id, tier aliases, tier bytes, block map or `BlockMapIterator`, lost storage, config properties, and build version.
- Implements `Iterator<RegisterWorkerPRequest>` via `hasNext()` and `next()`.
- `registerWithMaster()` opens the bidirectional stream and drives `registerInternal`.
- `abort()` handles stream abort/error propagation.
- Uses `mAckLatch`, `mFinishLatch`, `mBucket` semaphore with `MAX_BATCHES_IN_FLIGHT = 2`, and `AtomicReference<Throwable> mError`.

### Control Flow
The iterator emits a first request containing worker identity/static metadata/options and then location-block-list batches from `BlockMapIterator`, incrementing batch number. Registration starts a gRPC stream with a response observer. The worker sends requests while respecting the bucket semaphore so at most two batches are in flight. Master responses release permits/acknowledge progress; completion waits for finish latches and converts timeouts/errors into status exceptions.

### State and Persistence
State is per-registration stream: batch number, iterator position, flow-control permits, latches, observer, and error reference. It persists no data locally; the effect is the master’s worker registration state.

### Dependencies and Integration Points
Used by block master sync helpers during full worker registration. Depends on `BlockMapIterator`, gRPC block master service stubs, `RegisterWorkerPOptions`, build/config protobufs, and configuration timeout properties.

### Risks
- Registration correctness depends on precise latch/semaphore behavior; lost responses or observer errors can deadlock until configured timeout.
- Only two batches in flight limits memory but can constrain registration throughput for very large block maps.
- The class is both iterator and stream owner; reusing an instance after registration would be unsafe.

### Test Signals
`RegisterStreamerTest` covers request iteration, stream behavior, response/error handling, and timeout-like cases using mocked streams.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RegisterStreamer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RemoteBlockReader.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RemoteBlockReader.java

### Purpose
`RemoteBlockReader` adapts a remote worker `BlockInStream` to the worker `BlockReader` API for whole-block caching from another worker.

### Important APIs and Types
- Constructor takes `FileSystemContext`, block id/size, remote data source, and UFS fallback options.
- `getChannel()` lazily initializes the remote stream and returns a readable channel.
- `transferTo(ByteBuf)` streams bytes from the remote `BlockInStream`.
- `read(long,long)` is unsupported.
- `close()` closes stream/channel and increments remote-read metric.

### Control Flow
The first channel or transfer request calls `init`, which builds a `WorkerNetAddress` from the source socket and invokes `BlockInStream.createRemoteBlockInStream`. `transferTo` returns `-1` when no remaining bytes exist, otherwise writes up to the buffer’s writable bytes. Close is idempotent.

### State and Persistence
State is the lazy remote input stream/channel and closed flag. It does not write local files; `CacheRequestManager` copies from it into a `BlockWriter`.

### Dependencies and Integration Points
Created by `CacheRequestManager.cacheBlockFromRemoteWorker`. Uses client block stream APIs, Netty `ByteBuf`, metrics, and UFS options for fallback through the remote worker.

### Risks
- `getLength()` returns `mUfsOptions.getBlockSize()` rather than `mBlockSize`, so inconsistent options could report a mismatched length.
- Not thread-safe; concurrent channel/transfer/close calls could race lazy initialization and closure.
- Only channel/transfer access is supported, not positional reads.

### Test Signals
Remote caching tests can mock `CacheRequestManager.getRemoteBlockReader`. Broader remote block stream behavior is covered in client/block stream tests outside this file.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/RemoteBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/SpecificMasterBlockSync.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/SpecificMasterBlockSync.java

### Purpose
`SpecificMasterBlockSync` is the heartbeat executor for one specific block master in all-master registration mode. It asynchronously registers/re-registers the worker with that master, sends block heartbeat reports, handles master commands, and retries indefinitely on soft failures.

### Important APIs and Types
- Constructor takes `BlockWorker`, `BlockMasterClient`, and `BlockHeartbeatReporter`.
- `heartbeat(long)` performs registration if needed and sends heartbeat reports.
- `registerWithMasterInternal()` notifies worker id, obtains store meta, acquires registration lease, registers, updates state, and increments registration metric.
- `isRegistered()` exposes registration state.
- `handleMasterCommand(Command)` handles Free/Register/Nothing/Delete/Unknown commands.
- Nested `Metrics` contains registration success counter.

### Control Flow
When state is `NOT_REGISTERED`, heartbeat calls `registerWithMaster`, which clears pending heartbeat deltas and retries registration forever. Successful registration sets state to `REGISTERED`. For normal heartbeats, the sync generates and clears a report, calls helper heartbeat with current store meta and command callback, and updates last-success time on success. On heartbeat failure, if the report is too large it discards it and forces full re-registration; otherwise it merges the report back for retry. `Free` commands enqueue async block removal, while `Register` resets state.

### State and Persistence
State includes master address/client, worker id/address, worker state, async block remover, sync helper, last successful heartbeat timestamp, and heartbeat reporter. Persistent effects are through master registration/heartbeat RPCs and local block removals requested by master.

### Dependencies and Integration Points
Created by `BlockSyncMasterGroup`; uses `BlockMasterSyncHelper`, `AsyncBlockRemover`, `BlockWorker` metadata, master client RPCs, retry policies, and command protobufs.

### Risks
- Registration obtains full store metadata; TODO notes concurrent registration to all masters can cause OOM on large workers.
- Indefinite retries can block the heartbeat thread for a down master.
- On large failed reports, deltas are discarded and correctness relies on subsequent full registration.
- State is volatile but class is marked not thread-safe; external access should remain limited.

### Test Signals
`SpecificMasterBlockSyncTest` covers registration, heartbeat, re-registration, failure behavior, lease timeout behavior, and command handling. `TestSpecificMasterBlockSync` provides test hooks for heartbeat failure and registration counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/SpecificMasterBlockSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TestSpecificMasterBlockSync.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TestSpecificMasterBlockSync.java

### Purpose
`TestSpecificMasterBlockSync` is a visible-for-testing subclass of `SpecificMasterBlockSync` that exposes controllable heartbeat failures and a registration success counter for tests.

### Important APIs and Types
- `failHeartbeat()` and `restoreHeartbeat()` toggle a volatile failure flag.
- `getRegistrationSuccessCount()` returns an `AtomicInteger` count.
- Overrides `registerWithMasterInternal()` to increment the count after successful super registration.
- Overrides `beforeHeartbeat()` to throw `UnavailableRuntimeException` when failure is enabled.

### Control Flow
Tests can force normal heartbeat attempts to fail before the helper heartbeat RPC. Registration still uses the production path, and successful registration increments the test counter.

### State and Persistence
Only test-only in-memory state: failure flag and registration counter. No additional persistence beyond superclass behavior.

### Dependencies and Integration Points
Constructed by `BlockSyncMasterGroup` when `TEST_MODE` is true and directly by tests.

### Risks
- It lives under main sources, so production classpath includes test hooks gated only by test-mode construction.
- It changes timing/behavior only through `beforeHeartbeat`; registration failures still require mock/master setup.

### Test Signals
Used by all-master registration and specific master sync tests to assert re-registration and retry paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TestSpecificMasterBlockSync.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TieredBlockStore.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TieredBlockStore.java

### Purpose
`TieredBlockStore` is the thread-safe local block-store implementation for file-backed tiered worker storage. It coordinates metadata, file operations, block locks, allocation, eviction, management tasks, pin protection, event listeners, storage health removal, and session temp-block cleanup.

### Important APIs and Types
- Constructors create `BlockMetadataManager`, `BlockLockManager`, configured `Allocator`, block iterator listeners, and `ManagementTaskCoordinator`.
- Read/write lifecycle: `createBlock`, `createBlockWriter`, `requestSpace`, `commitBlock`, `commitBlockLocked`, `abortBlock`, `createBlockReader`.
- Mutation: `moveBlock`, `removeBlock`, `removeBlockInternal`, `freeSpace`, `removeDir`, `removeInaccessibleStorage`.
- Metadata: `getVolatileBlockMeta`, `getTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, `hasBlockMeta`, `hasTempBlockMeta`.
- Helpers: `validateBlockIntegrityForRead`, `allocateSpace`, `createBlockMetaInternal`, `moveBlockInternal`, `getUpdatedView`.

### Control Flow
Reads acquire a read block lock, read metadata under the metadata read lock, validate the physical file, and wrap `StoreBlockReader` with metrics and a lock-closing delegating reader. Corrupt/missing zero-length files are removed before throwing block-not-exist. Creates allocate space under metadata write lock, create temp metadata, and create the temp file. Commits acquire a write block lock, convert temp metadata to committed metadata, optionally pin the parent file id, and notify listeners. Allocation first tries requested/any locations, then may call synchronized `freeSpace` to evict blocks using the block iterator and a fresh `BlockMetadataEvictorView`. Moves allocate a destination temp placeholder, physically move the file, then update metadata. Storage checker removes inaccessible dirs and reports block/storage loss.

### State and Persistence
Persistent state is local block/temp files under worker tier directories plus in-memory metadata mirroring those files. Runtime state includes metadata and block lock managers, allocator, listener list, pinned inode set, metadata read/write lock, and management task coordinator.

### Dependencies and Integration Points
It is the main `LocalBlockStore` used by `MonoBlockStore`. It integrates with metadata classes, allocators, block iterators/annotators, file utilities, event listeners (`BlockHeartbeatReporter`, `BlockMetricsReporter`), management tasks, and session cleaner.

### Risks
- The lock hierarchy is subtle: block locks protect per-block IO/metadata while metadata locks protect global structures. New code must avoid inversion and long metadata-lock IO.
- `moveBlockInternal` has a TODO for rollback after IO/metadata failures; partial physical moves can be hard to recover.
- `freeSpace` is synchronized and can delete many blocks while allocation waits.
- `createBlockFile` grants full permissions based on configured worker data permissions; security posture depends on sticky dirs and config.
- Integrity validation only fails size mismatch when actual length is zero; nonzero mismatches are logged but tolerated.

### Test Signals
`TieredBlockStore` is exercised broadly by block read/write grpc tests, `ShortCircuitBlockReadHandlerTest`, management tier task tests, `MonoBlockStoreCommitBlockTest`, `UnderFileSystemBlockReaderTest`, and metadata/allocator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/TieredBlockStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsIOManager.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsIOManager.java

### Purpose
`UfsIOManager` provides asynchronous queued UFS reads with optional per-tag throughput quotas, reusable UFS input streams, and UFS throughput metrics. It is used by bulk block loading.

### Important APIs and Types
- Constructor stores a `UfsManager.UfsClient`.
- `start()` launches the scheduler loop.
- `close()` shuts down scheduler and IO executors.
- `setQuota(String tag, long throughput)` configures bytes/sec-like throughput limits.
- `read(ByteBuffer, offset, len, blockId, ufsPath, UfsReadOptions)` enqueues a `ReadTask` and returns a `CompletableFuture<Integer>`.
- Inner `ReadTask` opens/acquires UFS input stream, reads into the caller buffer, releases the stream, marks metrics, and completes the future.

### Control Flow
`read` validates offset/length/buffer capacity, rejects when the bounded queue is at capacity, returns completed zero for empty reads, creates/gets a tagged throughput meter, and enqueues a task. The scheduler thread takes tasks, checks quota against one-minute meter rate divided by 60, requeues if over quota, otherwise submits to the IO executor. `ReadTask` sets authenticated user when provided, acquires a cached stream at the requested offset, reads until requested length or EOF, releases the stream, marks metrics, and completes or fails the future.

### State and Persistence
State includes quota map, input-stream cache, bounded read queue, meters, scheduler executor, and fixed IO executor. It reads from UFS only; persistence occurs later when `MonoBlockStore.load` writes the buffer to local block storage.

### Dependencies and Integration Points
Created per mount by `UnderFileSystemBlockStore.getOrAddUfsIOManager`; used by `MonoBlockStore.load`. Integrates with UFS clients, `UfsInputStreamCache`, metrics, authenticated user context, and direct buffers owned by callers.

### Risks
- Queue capacity check uses `size() >= READ_CAPACITY` before `add`, which is racy under concurrency.
- Requeueing over-quota tasks can spin and starve other tags depending on queue ordering.
- `Channels.newChannel(inStream)` is recreated inside the read loop.
- The field typo `mBuffuer` is harmless but signals low polish.
- User context is set but not cleared in the task, which may matter on reused executor threads if the auth API is thread-local.

### Test Signals
Expected coverage is through load-path tests and any UFS IO manager unit tests. `getUsedThroughput` is visible for testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsIOManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsInputStreamCache.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsInputStreamCache.java

### Purpose
`UfsInputStreamCache` reuses seekable UFS input streams per file id to reduce open/close overhead for UFS block reads and load reads. Non-seekable UFSes or disabled cache mode fall back to always opening and closing streams.

### Important APIs and Types
- Constructor builds a Guava cache of resource id to `CachedSeekableInputStream` with maximum size, expire-after-access, and async removal listener.
- `acquire(UnderFileSystem, path, fileId, OpenOptions)` returns a cached or newly opened input stream positioned at the requested offset.
- `release(InputStream)` returns cached streams to available state or closes non-cached/expired streams.
- Inner `StreamIdSet` tracks in-use and available resource ids per file.

### Control Flow
Acquire exits early for non-seekable/disabled cache. Otherwise it cleans up expired entries, gets/creates a `StreamIdSet`, tries to atomically acquire an available cached stream id, seeks the stream to the requested offset, and returns it. If none is available, it generates a new random non-negative id, opens a seekable UFS stream, wraps it, and stores it in the cache. Release moves the id from in-use to available if still tracked; otherwise it closes the stream. The removal listener removes ids from tracking and closes only streams that were available, logging if an in-use stream expires.

### State and Persistence
State is in-memory cache and per-file id sets. It persists nothing. UFS stream resources remain open while cached and available.

### Dependencies and Integration Points
Used by `UnderFileSystemBlockReader` and `UfsIOManager`. Depends on UFS seekability, `OpenOptions`, Guava cache, async removal executor, and `CachedSeekableInputStream`.

### Risks
- In-use streams can expire from Guava cache; the listener removes them from tracking but does not close them until release, which is intentional but easy to mis-handle.
- `availableIds()` returns an unmodifiable view over the mutable set; iteration is protected by synchronizing on `streamIds` in current code.
- Cache key space uses random longs; collisions loop until free.
- Removal-thread lifecycle is not exposed for shutdown in this class.

### Test Signals
`UnderFileSystemBlockReaderTest` uses `UfsInputStreamCache` and covers stream reuse/caching via UFS reader behavior. Dedicated cache tests may exist outside the searched references.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UfsInputStreamCache.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockReader.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockReader.java

### Purpose
`UnderFileSystemBlockReader` is a `BlockReader` that reads a block range directly from UFS and opportunistically caches the block into local worker storage when the read starts at offset 0 and proceeds contiguously through the whole block.

### Important APIs and Types
- Static `create(...)` acquires UFS resource, constructs reader, and initializes stream/writer at the requested offset.
- `read(long offset, long length)` performs positional-style UFS reads and writes newly read contiguous bytes to the local temp block when caching.
- `transferTo(ByteBuf)` supports sequential streaming reads and cache writes.
- `close()` finalizes stream/resource and closes block writer after calling `updateBlockWriter(blockSize)`.
- Helpers `updateUnderFileSystemInputStream`, `updateBlockWriter`, and `cancelBlockWriter` manage UFS stream positioning and local cache eligibility.

### Control Flow
Initialization opens/acquires a UFS input stream at block offset plus read offset and creates a local temp block/writer only when offset is zero and caching is allowed. If future reads skip beyond the current writer position, caching is canceled and temp metadata is aborted. On reads/transfers, bytes are read from UFS, metrics are updated, and any contiguous bytes not yet written are appended after requesting space. Close calls `updateBlockWriter` at block size, which aborts incomplete cache writes if the full block was not read, releases the UFS input stream to the cache, closes the writer, closes UFS resource, and increments blocks-read-UFS counter.

### State and Persistence
State includes UFS block metadata, UFS resource, input stream position, optional local block writer, closed flag, initial block size, metrics, and local store reference. Persistent effects occur only when the reader successfully writes and closes a full local temp block for later commit by the UFS block store/worker close flow.

### Dependencies and Integration Points
Created by `UnderFileSystemBlockStore.createBlockReader`, used by `MonoBlockStore.createUfsBlockReader`, cache requests, and client UFS fallback reads. Integrates with `LocalBlockStore`, `UfsInputStreamCache`, UFS manager resources, metrics, and Netty buffers.

### Risks
- Cache correctness depends on contiguous full-block reads; any seek gap aborts caching.
- Exceptions while appending cache data cancel the writer but still let the UFS read continue.
- `read` allocates a byte array sized by requested bytes cast to int, so very large single read requests can stress heap.
- Close behavior can abort temp blocks if called before full read; callers must understand that partial reads are no-cache.

### Test Signals
`UnderFileSystemBlockReaderTest` covers create/read/offset behavior, caching, no-cache paths, transfer, cancellation on errors, and close behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockReader.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockStore.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockStore.java

### Purpose
`UnderFileSystemBlockStore` manages virtual UFS blocks opened by worker sessions. It tracks per-session/block UFS access state, creates UFS block readers, closes/releases those readers, cleans up sessions, and owns per-mount `UfsIOManager` instances for load operations.

### Important APIs and Types
- `acquireAccess(sessionId, blockId, OpenUfsBlockOptions)` creates a `UnderFileSystemBlockMeta` and stores `BlockInfo`.
- `createBlockReader(sessionId, blockId, offset, positionShort, options)` resolves UFS block paths, registers access, creates metrics, and creates `UnderFileSystemBlockReader`.
- `closeBlock` closes the reader inside `BlockInfo`.
- `releaseAccess` removes maps for a session/block.
- `cleanupSession` closes/releases all blocks for a session.
- `getOrAddUfsIOManager(long mountId)` lazily creates and starts per-mount UFS IO managers.
- `isNoCache` reads UFS block metadata flag.
- Inner `Key`, `BytesReadMetricKey`, and `BlockInfo` support map keys, metrics keys, and reader state.

### Control Flow
Access is registered under a `ReentrantLock` in both `mBlocks` and `mSessionIdToBlockIds`. Reader creation resolves fallback UFS block path when only `blockInUfsTier` is set, acquires access, retrieves `BlockInfo`, returns any still-open cached reader for that block/session, otherwise builds mount/user metrics and an `UnderFileSystemBlockReader`, then stores it in `BlockInfo`. Cleanup takes a snapshot-like reference to session block ids, then closes and releases each one; comments acknowledge a low-impact race.

### State and Persistence
State includes locked maps of active UFS blocks and session memberships, UFS read counters/meters, local store reference, UFS manager, per-mount IO manager map, and UFS input stream cache. It persists no block data directly; `UnderFileSystemBlockReader` may create local temp blocks through `LocalBlockStore`.

### Dependencies and Integration Points
Composed by `MonoBlockStore`; integrates with `UfsManager`, `UnderFileSystemBlockMeta`, `UnderFileSystemBlockReader`, `LocalBlockStore`, metrics, and session cleaner.

### Risks
- The lock protects maps only; `BlockInfo` reader state has its own synchronization. New code must preserve this split.
- `acquireAccess` rejects duplicate `(sessionId, blockId)` opens; clients opening multiple readers for the same pair can fail.
- `cleanupSession` iterates a set that can become stale after release; current behavior logs extra warnings rather than crashing.
- `BytesReadMetricKey.equals` calls `mUser.equals(that.mUser)`, which can throw if `mUser` is null despite null-user keys being possible.

### Test Signals
`UnderFileSystemBlockStoreTest` covers access acquisition/release, duplicate block handling, cleanup, reader creation, and no-cache state. `UnderFileSystemBlockReaderTest` covers reader-side behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/UnderFileSystemBlockStore.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/WorkerMasterRegistrationState.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/WorkerMasterRegistrationState.java

### Purpose
`WorkerMasterRegistrationState` is the finite state enum for a worker’s registration lifecycle with a specific block master in all-master registration mode.

### Important APIs and Types
- Values: `NOT_REGISTERED`, `REGISTERING`, `REGISTERED`.

### Control Flow
`SpecificMasterBlockSync` starts at `NOT_REGISTERED`, sets `REGISTERING` during full registration, sets `REGISTERED` after successful registration, and resets to `NOT_REGISTERED` when a master requests registration or a heartbeat report is too large to retry incrementally.

### State and Persistence
The enum has no fields. Persistence is only the volatile enum field in `SpecificMasterBlockSync`.

### Dependencies and Integration Points
Used by `SpecificMasterBlockSync.isRegistered`, `heartbeat`, and registration methods.

### Risks
- The enum is intentionally minimal; any new intermediate/error states require changes to heartbeat control flow and tests.

### Test Signals
Registration state transitions are covered by `SpecificMasterBlockSyncTest` and all-master registration tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/WorkerMasterRegistrationState.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/Allocator.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/Allocator.java

### Purpose
`Allocator` is the public API for choosing a storage directory for new or moved blocks from a metadata view and location constraint.

### Important APIs and Types
- `Allocator.Factory.create(BlockMetadataView)` instantiates the configured allocator class from `WORKER_ALLOCATOR_CLASS`.
- `allocateBlockWithView(long blockSize, BlockStoreLocation location, BlockMetadataView view, boolean skipReview)` returns a `StorageDirView` or null.

### Control Flow
Factory validates the view and uses `CommonUtils.createNewClassInstance` with a `BlockMetadataView` constructor. Implementations evaluate location wildcards, available bytes, medium constraints, and optional `Reviewer` acceptance. `skipReview` is used after deterministic frees or forced locations.

### State and Persistence
The interface itself holds no state and persists nothing. Implementations typically keep the latest metadata view and a reviewer.

### Dependencies and Integration Points
Created by `TieredBlockStore` and `BlockMetadataManager` legacy evictor emulation. The allocator chooses dirs used by `TieredBlockStore.createBlockMetaInternal`, `requestSpace`, and move logic.

### Risks
- Misconfigured allocator class fails at runtime during worker/block metadata initialization.
- Returning null is part of normal no-space flow; callers must decide when to evict or throw.
- Reviewer logic is currently coupled to allocator interface, with a TODO to refactor.

### Test Signals
`AllocatorContractTest`, allocator-specific tests, and `ReviewerFactoryTest` cover factory defaults and allocation contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/Allocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/GreedyAllocator.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/GreedyAllocator.java

### Purpose
`GreedyAllocator` is a simple non-thread-safe allocator that returns the first directory in tier/dir iteration order that can fit the requested block and passes review.

### Important APIs and Types
- Constructor takes an initial `BlockMetadataView` and creates a `Reviewer`.
- `allocateBlockWithView` swaps in the provided view and delegates to private `allocateBlock`.
- `allocateBlock` handles any-tier/any-dir, any-dir-in-tier, and specific-dir locations.

### Control Flow
For any-tier requests, it iterates tiers in view order and dirs in dir order, respecting medium constraints and available bytes, and returns the first accepted dir. For any-dir-in-tier, it scans only that tier. For specific-dir requests, it skips reviewer checks and returns the dir if capacity is sufficient.

### State and Persistence
State is the current metadata view and reviewer. It persists nothing and makes no metadata changes; callers later create temp metadata in the selected dir.

### Dependencies and Integration Points
Can be configured by `WORKER_ALLOCATOR_CLASS` and used by `TieredBlockStore`. Reviewer acceptance integrates with allocation policy extensions such as probabilistic buffer review.

### Risks
- First-fit behavior can concentrate allocations in early dirs/tiers and cause imbalance.
- Not thread-safe; `mMetadataView` is mutated per call.
- Specific-dir allocations bypass reviewer by design.

### Test Signals
Allocator contract/base tests exercise expected allocation behavior. Reviewer tests cover factory interaction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/GreedyAllocator.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/MaxFreeAllocator.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/MaxFreeAllocator.java

### Purpose
`MaxFreeAllocator` is the default-style allocator that chooses the directory with the most free space within the highest acceptable tier for any-tier allocations, while respecting location and medium constraints.

### Important APIs and Types
- Constructor stores metadata view and reviewer.
- `allocateBlockWithView` updates the current view and delegates to `allocateBlock`.
- `allocateBlock` handles any-tier/any-dir, any-dir-in-tier, and specific-dir cases.
- `getCandidateDirInTier` returns the dir in a tier with maximum available bytes greater than or equal to requested size.

### Control Flow
Any-tier allocation scans tiers in order. For each tier, it chooses the maximum-free candidate dir matching medium and capacity; if accepted by reviewer or review is skipped, it stops. If reviewer rejects that tier’s best dir, it moves to lower tiers rather than trying second-best dirs in the same tier. Any-dir-in-tier chooses the max-free dir in that tier and applies review. Specific-dir returns the dir if it has enough bytes and skips review.

### State and Persistence
State is the current metadata view and reviewer. It persists nothing and does not mutate metadata.

### Dependencies and Integration Points
Created through `Allocator.Factory` by `TieredBlockStore`. Works with `BlockMetadataAllocatorView` and `BlockMetadataEvictorView` snapshots and reviewer implementations.

### Risks
- For any-tier allocations, reviewer rejection of the max-free dir skips other viable dirs in the same tier.
- Not thread-safe due to mutable `mMetadataView`.
- Specific-dir allocations bypass reviewer, so forced moves/expansions can ignore buffer policies.

### Test Signals
Allocator contract tests cover allocation semantics. Reviewer factory tests validate default reviewer/allocator wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/main/java/alluxio/worker/block/allocator/MaxFreeAllocator.java -->
