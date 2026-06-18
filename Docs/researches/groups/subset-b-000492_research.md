# subset-b-000492 Research

Grouped source research for Alluxio worker block tests and helpers. Each section preserves the source path in its title and is bounded by reconciliation markers for source-tree-aligned per-file splitting.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataManagerTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataManagerTest.java

**Purpose:** Unit tests `BlockMetadataManager`, the in-memory model for worker tier, directory, committed block, and temporary block metadata. The suite uses a two-tier MEM/HDD configuration with explicit capacities and media types.

**Important APIs:** Exercises `createBlockMetadataManager`, `getTier`, `getDir`, `getTiers`, `getTiersBelow`, `getAvailableBytes`, `addTempBlockMeta`, `abortTempBlockMeta`, `commitTempBlockMeta`, `removeBlockMeta`, `moveBlockMeta`, `resizeTempBlockMeta`, and `getBlockStoreMeta`.

**Control flow:** `before` builds temporary tier directories via `TieredBlockStoreTestUtils.setupConfWithMultiTier`, disables tier management, then constructs metadata. Tests add temp metas, commit them into `BlockMeta`, move committed blocks through destination temp metas, and assert optional lookups or expected exceptions.

**State and persistence:** State is the metadata graph plus temp/committed block accounting inside `StorageDir`. It does not validate physical file movement directly, except through metadata-derived paths and block store aggregate counters.

**Dependencies and integration:** Depends on global Alluxio configuration, storage meta classes, `BlockStoreLocation`, Guava `ImmutableMap`, JUnit rules, and runtime exception messages. It is a foundation signal for allocators, evictors, and tiered block store behavior.

**Risks:** Global configuration mutation can leak if tests are reordered without rules. The move tests rely on destination temp metadata being removed, so regressions in move cleanup or capacity accounting would cascade into eviction and block store tests.

**Test signals:** Strong coverage of lookup, capacity aggregation, temp-to-committed lifecycle, same-dir/different-dir moves, out-of-space exception messages, resize, and tier-level store meta maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataViewTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataViewTest.java

**Purpose:** Tests `BlockMetadataEvictorView`, the read/filter view used by eviction and allocation logic. It verifies that view objects mirror `BlockMetadataManager` while hiding pinned or locked blocks from eviction.

**Important APIs:** Covers `getTierView`, `getTierViews`, `getTierViewsBelow`, `getAvailableBytes`, `getBlockMeta`, `isBlockEvictable`, `isBlockPinned`, `isBlockLocked`, and view equivalence with `StorageTierEvictorView`.

**Control flow:** Setup creates a default metadata manager and spies the evictor view. Tests compare view results to backing manager data, add a committed block directly to a `StorageDir`, then alter `isBlockPinned` and `isBlockLocked` spy responses to confirm filtering behavior.

**State and persistence:** The view holds pinned inode and locked block sets; it does not persist state. Test state lives in temporary tier directories and committed block metadata.

**Dependencies and integration:** Uses `BlockId.getFileId` to map block IDs to pin inodes, Mockito for selective method stubbing, and metadata view classes consumed by allocators and evictors.

**Risks:** A regression that exposes pinned or locked blocks would allow eviction of protected data. The equivalence helpers also protect directory-level available, capacity, committed, evictable block, and evictable byte calculations.

**Test signals:** Good coverage for missing tiers/blocks, tier view construction, pinned/locked filtering, and stable view equivalence after metadata changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockMetadataViewTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreLocationTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreLocationTest.java

**Purpose:** Unit tests location matching semantics for worker block storage. `BlockStoreLocation` represents any tier, any directory within a tier, any tier with a medium type, or a concrete tier/directory/medium target.

**Important APIs:** Exercises constructor accessors, `anyTier`, `anyDirInTier`, `anyDirInAnyTierWithMedium`, `belongsTo`, and `equals`.

**Control flow:** Tests construct wildcard and concrete MEM/HDD/SSD locations, then evaluate the `belongsTo` relation across wildcard-to-specific and specific-to-wildcard cases. Equality checks confirm only identical location shape and tier/dir values compare equal.

**State and persistence:** No persisted state; all behavior is immutable value-object comparison.

**Dependencies and integration:** Uses Alluxio medium constants and is foundational to allocator, evictor, tier movement, and block metadata location APIs.

**Risks:** Matching direction is easy to invert: concrete locations should belong to broader targets, while broad wildcard locations should not belong to narrower targets. Medium-aware wildcards add another axis that can silently affect placement.

**Test signals:** Covers location creation, wildcard containment, medium-type matching, and equality/non-equality combinations used by the rest of the block worker tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreLocationTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreMetaTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreMetaTest.java

**Purpose:** Tests `DefaultBlockStoreMeta` aggregation over worker storage. It validates block listings, directory/tier capacities, used bytes, and full-vs-summary metadata behavior after committing test blocks.

**Important APIs:** Covers `getBlockList`, `getCapacityBytes`, `getCapacityBytesOnDirs`, `getCapacityBytesOnTiers`, `getNumberOfBlocks`, `getUsedBytes`, `getUsedBytesOnDirs`, and `getUsedBytesOnTiers`.

**Control flow:** Setup creates default tiered metadata, repeatedly caches ten committed blocks into the first MEM directory, then constructs both normal and full store meta objects. Tests independently traverse `StorageTier` and `StorageDir` structures to build expected maps.

**State and persistence:** Test helper writes temp files and commits metadata, so store meta derives from real committed block accounting. Full meta includes detailed block and directory-location maps; non-full meta omits heavyweight block lists while preserving capacity/usage totals.

**Dependencies and integration:** Depends on `TieredBlockStoreTestUtils.cache`, Alluxio configuration, `Pair`, and storage meta classes. Its output shape is consumed by worker registration and heartbeat paths.

**Risks:** Incorrect aggregation can misreport worker capacity to masters, skew allocation, or hide blocks during registration. Full and non-full modes must diverge only where intended.

**Test signals:** Strong map-level checks for block IDs, total capacity, per-dir/per-tier capacity, committed block count, and used-byte accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockStoreMetaTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockWorkerMetricsTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockWorkerMetricsTest.java

**Purpose:** Verifies worker block metric gauges registered by the block worker metrics layer, especially cache-related counters visible through `MetricsSystem`.

**Important APIs:** Uses metric keys/gauge lookup through the metrics registry and validates cached block metric behavior after manipulating block worker/store state.

**Control flow:** The test constructs or mocks a block worker/store environment, obtains gauges by metric name, triggers cache-relevant state, and reads gauge values directly from the metric registry.

**State and persistence:** No durable persistence. Runtime state is metric registration plus in-memory block/store counters; failures generally indicate stale gauge functions or missing metric registration.

**Dependencies and integration:** Integrates with Codahale metrics, Alluxio `MetricKey`, `MetricsSystem`, and block worker/store metadata. These gauges feed operational monitoring and worker health visibility.

**Risks:** Metrics tests can be order-sensitive because metric registries are process-global. Gauge values must reflect live store state rather than captured snapshots, otherwise monitoring can silently drift.

**Test signals:** Provides a focused regression signal that block worker metrics remain registered and compute expected cache counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/BlockWorkerMetricsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/CacheRequestManagerTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/CacheRequestManagerTest.java

**Purpose:** Tests `CacheRequestManager`, which turns cache RPC requests into local UFS or remote-worker reads and materializes blocks in the worker block store.

**Important APIs:** Exercises `submitRequest`, async cache handling, `getRemoteBlockReader`, `DefaultBlockWorker.cache`, and `InStreamOptions.getOpenUfsBlockOptions`.

**Control flow:** Setup creates a real temporary root UFS file, mocked master clients, a `TieredBlockStore` wrapped by `MonoBlockStore`, a spied `DefaultBlockWorker`, and a spied cache manager. Tests submit sync/async requests whose source host is either local or fake-remote; remote cases stub a `RemoteBlockReader` channel that immediately EOFs.

**State and persistence:** Local tier storage and UFS temp files are real. Successful cache requests should create block metadata in the block store; async tests wait until the block appears.

**Dependencies and integration:** Uses Alluxio file metadata (`URIStatus`, `FileInfo`, `FileBlockInfo`), gRPC `CacheRequest`, UFS manager/client wiring, `GrpcExecutors.CACHE_MANAGER_EXECUTOR`, network hostname resolution, Mockito, and byte-buffer utilities.

**Risks:** Local-host detection changes source selection. Async cache depends on executor scheduling and wait timeouts. Remote reader mocks only EOF, so data-integrity coverage for remote transfer is limited here.

**Test signals:** Confirms all four local/remote and sync/async request paths result in cached block metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/CacheRequestManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerExceptionTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerExceptionTest.java

**Purpose:** Tests how `DefaultBlockWorker.load` translates UFS open failures and timeouts into `BlockStatus` error codes instead of crashing the batch load future.

**Important APIs:** Exercises `DefaultBlockWorker.load`, `UnderFileSystem.openExistingFile`, `AlluxioHdfsException.fromUfsException`, `OpenOptions`, and gRPC `BlockStatus` codes.

**Control flow:** Setup builds a worker with mocked UFS manager returning a mocked UFS. `loadFailure` programs sequential `openExistingFile` failures: Alluxio HDFS exception, runtime exception, and IOException; each load call should return one failure status. `loadTimeout` blocks longer than the RPC keepalive timeout and expects DEADLINE_EXCEEDED.

**State and persistence:** No real data is read; state is mocked exception sequencing and returned status lists. The block store is real enough to satisfy `DefaultBlockWorker` construction through `MonoBlockStore`.

**Dependencies and integration:** Integrates worker load with UFS exception mapping, status codes, master/client mocks, and configuration-driven timeout behavior.

**Risks:** Error translation must preserve useful status codes for callers. Timeout test depends on configuration duration and sleeps, so slow environments could affect runtime.

**Test signals:** Covers wrapped UFS exceptions, generic runtime/IO failures, and operation timeout handling in batch load.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerExceptionTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTest.java

**Purpose:** Main unit/integration-style test suite for `DefaultBlockWorker`, covering worker identity, block lifecycle operations, master commits, local and fallback reads, UFS load/cache, metadata reporting, configuration, pin updates, and session cleanup.

**Important APIs:** Exercises `askForWorkerId`, `getWorkerId`, `getWorkerInfo`, `createBlock`, `abortBlock`, `commitBlock`, `commitBlockInUfs`, `createBlockWriter`, `getReport`, `getStoreMeta`, `getStoreMetaFull`, `removeBlock`, `requestSpace`, `updatePinList`, `getFileInfo`, `createBlockReader`, `createUfsBlockReader`, `load`, `cache`, `getConfiguration`, and `cleanupSession`.

**Control flow:** Tests build on `DefaultBlockWorkerTestBase`. They create temp blocks in MEM/HDD, write through block writers, commit or abort, simulate master failures with Mockito, and assert local store metadata. Read tests hold readers to validate lock behavior; UFS fallback and load tests create real files and validate increasing-byte data.

**State and persistence:** Uses real temporary local tier directories and UFS files. Persistent effects are temp/committed block files, metadata, master-client method invocations, and lock manager state.

**Dependencies and integration:** Integrates block master/file-system master mocks, `MonoBlockStore`, `TieredBlockStore`, `NoopUfsManager`, `Protocol.OpenUfsBlockOptions`, gRPC load/cache messages, metrics/configuration, and byte-buffer utilities.

**Risks:** Many tests mutate global configuration through the base rule. Random block/session IDs reduce collision risk but can make reproducing failures harder. Async cache and reader-lock tests depend on timing.

**Test signals:** Broad regression signal for happy paths, retry/idempotent commit, master failure propagation, no-space errors, lock cleanup, duplicate load failure, fallback-to-UFS caching, missing-block exceptions, and cache sync/async correctness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTestBase.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTestBase.java

**Purpose:** Shared fixture for `DefaultBlockWorker` tests. It centralizes two-tier worker storage, mocked master clients, UFS mounts, a real `MonoBlockStore`, and cache helper behavior.

**Important APIs:** Provides `before`, `cacheBlock`, `createMockBlockMasterClient`, and `createMockFileSystemMasterClient`, plus constants for block size, worker ID, UFS mount IDs, worker address, and invalid worker ID.

**Control flow:** The setup creates MEM/HDD temp directories, applies a `ConfigurationRule`, mocks block master heartbeat and worker-ID responses, constructs a spied `TieredBlockStore` and `MonoBlockStore`, registers two UFS mounts, writes an increasing-byte UFS file for load tests, and instantiates `DefaultBlockWorker`.

**State and persistence:** Creates real temporary local storage and UFS files. The helper `cacheBlock` writes random data to UFS, issues a cache request, waits for async completion if requested, and reads the cached local block back.

**Dependencies and integration:** Bridges `DefaultBlockWorker`, `BlockMasterClientPool`, `FileSystemMasterClient`, `Sessions`, `NoopUfsManager`, `NetworkAddressUtils`, `WaitForOptions`, and local block readers.

**Risks:** Because the fixture is shared, configuration mistakes affect many tests. The helper validates data with `ByteBuffer.compareTo`, which depends on buffer position/limit correctness.

**Test signals:** Enables consistent coverage for worker lifecycle, local tier placement, UFS fallback/load/cache, heartbeat defaults, and pin-list defaults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/DefaultBlockWorkerTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/MonoBlockStoreCommitBlockTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/MonoBlockStoreCommitBlockTest.java

**Purpose:** Tests commit event ordering and failure boundaries in `MonoBlockStore.commitBlock`, where local commit and master commit are separate domains.

**Important APIs:** Exercises `MonoBlockStore.commitBlock`, `TieredBlockStore.commitBlockInternal`, `BlockMasterClient.commitBlock`, `registerBlockStoreEventListener`, and listener callbacks `onCommitBlockToLocal` and `onCommitBlockToMaster`.

**Control flow:** Setup builds metadata, lock manager, mocked block master client/pool, a test storage dir, and a spied event listener. `prepareBlockStore` creates a temp block, writes data through a block writer, and registers the listener. Tests cover both commits succeeding, master commit failing after local commit, and local commit failing before master notification.

**State and persistence:** Creates a real temp block file and updates local metadata. Master state is mocked; event listener invocations are the main observable side effect.

**Dependencies and integration:** Depends on `TieredBlockStoreTestUtils`, `BlockWriter`, `UfsManager`, `AtomicReference` worker ID, Mockito answers, and Alluxio status exceptions.

**Risks:** Incorrect listener ordering can cause heartbeat/reporting inconsistencies. A master failure after local commit leaves local state changed but should not emit a master-commit event.

**Test signals:** Focused coverage of local/master commit callback semantics under success and both failure points.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/MonoBlockStoreCommitBlockTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/NoopBlockWorker.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/NoopBlockWorker.java

**Purpose:** Test double implementing `BlockWorker` with no operational behavior. It is useful where a component needs a worker interface but the test does not care about block storage side effects.

**Important APIs:** Implements worker methods for block lifecycle, cache/load, metadata/reporting, metrics/configuration, service registration, worker identity/address, dependencies, start/stop/close, and session cleanup.

**Control flow:** Most mutating methods are no-ops. Many accessors return `null`, empty collections, or completed futures, so callers must only use methods relevant to their test path.

**State and persistence:** It stores no state and performs no persistence. It does not track blocks, sessions, metrics, or worker identity.

**Dependencies and integration:** Depends on the full `BlockWorker` interface and gRPC/wire types, but intentionally avoids `TieredBlockStore`, UFS, and master clients.

**Risks:** Because many accessors return `null`, this double can hide missing setup until a code path dereferences a value. It is safest for tests that only need an object identity or no-op side-effect sink.

**Test signals:** Not a test itself; its value is enabling isolated tests of collaborators without spinning a real block worker.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/NoopBlockWorker.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/PinListSyncTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/PinListSyncTest.java

**Purpose:** Tests synchronization of pinned inode lists from the file-system master into the block worker.

**Important APIs:** Exercises `PinListSync`, `FileSystemMasterClient.getPinList`, and `BlockWorker.updatePinList`.

**Control flow:** The test uses a temporary folder/rule fixture, mocks a file-system master client returning a pin set, constructs the sync task with a block worker, runs the heartbeat/sync method, and verifies the worker receives the exact set.

**State and persistence:** No durable state. Runtime state is the pin set returned by the master client and the worker's update call.

**Dependencies and integration:** Integrates worker heartbeat-side synchronization with file-system master metadata and block eviction protection. Often paired indirectly with `BlockMetadataEvictorView` tests that enforce pinned-block filtering.

**Risks:** Missed or stale pin-list updates could let eviction remove blocks for pinned files. Error handling is important because master calls are remote and can fail in production.

**Test signals:** Focused signal that the sync task delegates master pin data to the block worker update hook.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/PinListSyncTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/RegisterStreamerTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/RegisterStreamerTest.java

**Purpose:** Tests streamed worker registration to the block master over gRPC, including response deadlines, completion handling, server errors, and successful multi-request registration.

**Important APIs:** Exercises `RegisterStreamer.registerWithMaster`, `BlockMasterWorkerServiceGrpc.registerWorkerStream`, streamed `RegisterWorkerPRequest/Response`, and configuration keys controlling stream timeouts, deadline, completion timeout, and batch size.

**Control flow:** Each test starts an in-process gRPC server with a custom `StreamObserver` supplier and creates a channel-backed `RegisterStreamer`. Server observers either never respond, respond without completing, error early, complete early, error on completion, or respond and complete successfully.

**State and persistence:** No durable state. Runtime state includes gRPC server/channel lifecycle, request counts per worker ID, and stream observer callbacks.

**Dependencies and integration:** Uses Alluxio gRPC test utilities, `ConfigurationRule`, NOSASL auth, worker store metadata maps, worker config list, and Java streams to generate block IDs.

**Risks:** Streaming registration is timing-sensitive; deadlines must fail promptly without hanging tests. Early server completion/error handling must map to the correct Alluxio status exception.

**Test signals:** Strong coverage for single and concurrent request timeouts, missing completion, early server error, early completion cancellation, completion-time error, and successful request count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/RegisterStreamerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/SpecificMasterBlockSyncTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/SpecificMasterBlockSyncTest.java

**Purpose:** Tests `SpecificMasterBlockSync`, the per-master heartbeat/registration coordinator for a block worker.

**Important APIs:** Exercises `heartbeat`, `isRegistered`, block master `register`, `registerWithStream`, `heartbeat`, `acquireRegisterLeaseWithBackoff`, and `BlockHeartbeatReporter.generateReportAndClear`.

**Control flow:** The single test configures heartbeat report threshold, uses a custom reporter that adds one removed block per report generation, and a custom block master client with toggles for flaky registration, register commands, and heartbeat failures. It verifies initial registration, register-command reset for both streaming and non-streaming modes, retry behavior on heartbeat failure, and later re-registration.

**State and persistence:** Runtime state includes registration flag, heartbeat call count, reporter accumulated removals, and client booleans indicating which registration path ran. No durable state.

**Dependencies and integration:** Uses `BlockWorker` mock returning store meta, report, address, and worker ID. Integrates heartbeat report sizing, registration lease hooks, master commands, and stream-registration configuration.

**Risks:** Incorrect registration state transitions can leave workers unregistered or repeatedly re-registering. Report clearing on failures must avoid losing block changes while still preventing unbounded reports.

**Test signals:** Covers flaky registration recovery, master-driven re-registration, threshold-limited heartbeat retries, and both legacy and stream registration paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/SpecificMasterBlockSyncTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTest.java

**Purpose:** Extensive tests for `TieredBlockStore`, covering local block storage lifecycle, locking, move/free-space behavior, allocation edge cases, reserved space, pinned blocks, and failed storage removal.

**Important APIs:** Exercises `pinBlock`, `commitBlock`, `abortBlock`, `moveBlock`, `removeBlock`, `freeSpace`, `requestSpace`, `createBlock`, `createBlockWriter`, `hasBlockMeta`, `hasTempBlockMeta`, `getBlockStoreMeta`, `getBlockStoreMetaFull`, and `removeInaccessibleStorage`.

**Control flow:** Setup reloads configuration, creates a default two-tier MEM/SSD layout, metadata manager, lock manager, block store, iterator, and test dirs. Tests use helpers to create temp or committed block files, then perform operations and assert metadata plus physical temp/commit path presence.

**State and persistence:** Uses real temp files in tier directories, committed/temp metadata, lock manager state, pinned block state, and directory capacity accounting. Failed-storage test deletes a directory and checks store meta shrinkage.

**Dependencies and integration:** Depends on allocator/evictor configuration, block iterator notifications, `EvictionPlan`, `Evictor`, retry/concurrency utilities, `FileUtils`, and Alluxio exception messages.

**Risks:** This is a high-blast-radius component. Regressions can corrupt block files, violate lock safety, overuse reserved bytes, move blocks into full destinations, evict pinned/locked data, or misreport failed storage.

**Test signals:** Broad coverage of success paths, same-location no-op, tier move full errors, concurrent free-space calls, pinned/locked eviction failures, request-space failures, medium-aware allocation, relaxed versus forced placement, reserved-space moves, duplicate blocks, wrong-session errors, and inaccessible directory cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTestUtils.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTestUtils.java

**Purpose:** Shared utility class for constructing tiered-store configurations and seeding local block data in worker block tests.

**Important APIs:** Provides default tier constants, `setupConfWithMultiTier`, `setupConfWithSingleTier`, `setupDefaultConf`, `defaultMetadataManager`, `defaultMetadataManagerView`, `cache` overloads, `cache2`, `createTempBlock`, `getDefaultTotalCapacityBytes`, and `getDefaultDirNum`.

**Control flow:** Configuration helpers validate array dimensions, create directory hierarchies under a base temp dir, and set tier alias/path/quota/medium properties. Cache helpers create temp metadata, write increasing bytes through `LocalFileBlockWriter`, move temp files to committed paths, commit metadata, and optionally notify event listeners or block iterators.

**State and persistence:** Mutates global Alluxio configuration and creates real local directories/files. It also mutates `BlockMetadataManager` and `LocalBlockStore` state.

**Dependencies and integration:** Used by metadata, view, block-store, allocator, annotator, and sync tests. Depends on `PathUtils`, `FileUtils`, `BufferUtils`, `DefaultTempBlockMeta`, `LocalFileBlockWriter`, and `BlockIterator` listener contracts.

**Risks:** Because it bypasses some production store methods in `cache2`, tests using it must manually trigger listeners when iterator state matters. Global configuration mutation makes cleanup/rule discipline important.

**Test signals:** Not a test itself, but it provides deterministic tier layouts and block data for most block worker unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/TieredBlockStoreTestUtils.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsInputStreamCacheTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsInputStreamCacheTest.java

**Purpose:** Tests `UfsInputStreamCache`, which reuses seekable UFS input streams and closes non-reusable or expired streams.

**Important APIs:** Exercises `acquire`, `release`, UFS `isSeekable`, `openExistingFile`, `SeekableUnderFileInputStream.seek`, cache expiration property, and concurrent checkout/checkin behavior.

**Control flow:** Setup creates a mocked UFS that is seekable and returns a sequence of mocked seekable streams. Tests cover non-seekable streams closing on release, same-file reuse with seek to requested offset, multiple simultaneous checkouts opening multiple streams, expiration-triggered close, release after expiration for same/different file, and concurrent repeated acquire/release loops.

**State and persistence:** State is in-memory cache entries keyed by file identity/path and stream checkout status. No real files are read.

**Dependencies and integration:** Uses `ConfigurationRule` for expiration time, Mockito invocation introspection, `ConcurrencyUtils`, and UFS open options. This cache is consumed by under-file-system block readers.

**Risks:** Stream reuse is concurrency-sensitive. Incorrect expiration or release handling can leak file descriptors, close in-use streams, or seek a stream for the wrong file.

**Test signals:** Covers reuse, non-reuse, expiration cleanup, release-after-expire races, and concurrent seek counts under no-expiration and expiration settings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsInputStreamCacheTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsIoManagerTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsIoManagerTest.java

**Purpose:** Tests `UfsIOManager`, the asynchronous UFS block read manager used for loading blocks from UFS into buffers with optional concurrency quota.

**Important APIs:** Exercises UFS read submission, `CompletableFuture` completion, `UfsReadOptions`, buffer range validation, and quota/concurrency handling.

**Control flow:** Setup creates a real temporary root UFS file with increasing-byte content, constructs a UFS client, and creates an `UfsIOManager`. Tests request full blocks, partial ranges, second block offsets, overlapping reads, and reads with quota limits; each validates returned `ByteBuffer` content.

**State and persistence:** Uses a real temp UFS file. Runtime state is the manager's async task tracking and metrics/throughput wiring; no local block metadata is persisted by this manager alone.

**Dependencies and integration:** Integrates `UnderFileSystem`, `UfsManager.UfsClient`, `UfsReadOptions`, `CompletableFuture`, `Meter`, configuration root UFS, and `BufferUtils`.

**Risks:** Offset math is central: block ID, block size, and file offset must map to the correct bytes. Quota enforcement must not deadlock or incorrectly truncate reads.

**Test signals:** Provides data-integrity checks for full, partial, offset, overlap, and quota-constrained UFS reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UfsIoManagerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockReaderTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockReaderTest.java

**Purpose:** Tests `UnderFileSystemBlockReader`, which reads UFS blocks and opportunistically caches fully read blocks into the local block store.

**Important APIs:** Exercises `UnderFileSystemBlockReader.create`, `read`, `transferTo`, `close`, `getLocation`, `LocalBlockStore.createBlock`, `requestSpace`, `commitBlock`, `pinBlock`, and metrics counters/meters for UFS bytes read.

**Control flow:** Setup writes a two-block increasing-byte UFS file, builds a local `TieredBlockStore`, UFS client, input-stream cache, open options, block meta, and metrics. Tests read full or partial ranges, overlap reads until a full block is covered, disable caching with `noCache`, inject local create/request-space failures, transfer to Netty `ByteBuf`, and validate the cached temp block after close.

**State and persistence:** Uses real UFS and local worker storage. Full reads should leave a temp block that can be committed and read locally; partial reads and cache failures should not leave local metadata.

**Dependencies and integration:** Integrates UFS client/cache, local block store, Netty pooled buffers, Alluxio metrics tags, byte-buffer utilities, and open UFS block options.

**Risks:** Partial coverage tracking and cache-on-close behavior are subtle. Cache failures must not break read success. Netty buffers require release to avoid leaks.

**Test signals:** Strong coverage for full/partial/offset/overlap reads, no-cache, local cache resource exhaustion, `transferTo`, local cached data correctness, and reader location.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockReaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockStoreTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockStoreTest.java

**Purpose:** Tests `UnderFileSystemBlockStore`, the access-control and reader factory layer for UFS-resident blocks.

**Important APIs:** Exercises `acquireAccess`, duplicate access handling, `releaseAccess`, `createBlockReader`, no-cache option handling, session cleanup, and reader close behavior.

**Control flow:** Setup creates a temporary file, mocked local block store, a `NoopUfsManager` mount, and `OpenUfsBlockOptions` with max UFS read concurrency. Tests acquire up to the configured concurrency, reject duplicate/session-over-limit cases, release and reacquire, create readers over a real file, verify no-cache metadata, clean session access records, and close readers.

**State and persistence:** Runtime state is access tracking by session/block and reader lifecycle. The UFS file is real; local block store is mocked.

**Dependencies and integration:** Integrates UFS manager mounts, open options, local block store, `BlockReader`, temporary files, and exception types such as duplicate block/not found paths.

**Risks:** Access leaks can permanently exhaust UFS concurrency for a block. Cleanup must release all session-held access. Reader creation must honor no-cache and block metadata options.

**Test signals:** Covers concurrency caps, duplicate acquisition, release, reader creation/data, no-cache behavior, cleanup by session, and reader close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/UnderFileSystemBlockStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorContractTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorContractTest.java

**Purpose:** Defines contract tests that all `Allocator` implementations in the allocator package must satisfy.

**Important APIs:** Uses package scanning to discover `Allocator` implementation classes, sets `WORKER_ALLOCATOR_CLASS`, calls `Allocator.Factory.create`, and validates allocation through `assertTempBlockMeta`.

**Control flow:** `before` extends `AllocatorTestBase` setup, then uses Guava `ClassPath` to find classes implementing `Allocator`. Tests iterate each strategy, reset the metadata view, and verify oversized allocations fail, valid allocations succeed for tier-specific and any-tier targets, and allocation still works after deleting one directory from each tier.

**State and persistence:** Uses temporary tier directories and metadata views from the base class. Directory deletion mutates in-memory `StorageTier` lists to simulate failed/removed dirs.

**Dependencies and integration:** Depends on reflection/classpath scanning, global configuration, allocator factory, `BlockMetadataEvictorView`, and base helper assertions.

**Risks:** Reflection can miss implementations if classloader packaging changes. Contract coverage protects common behavior but not exact placement policy.

**Test signals:** Ensures all allocator strategies honor capacity boundaries, tier constraints, any-tier behavior, and dynamic directory removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorContractTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorFactoryTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorFactoryTest.java

**Purpose:** Tests `Allocator.Factory` class selection from Alluxio configuration and default allocator behavior.

**Important APIs:** Exercises `Allocator.Factory.create`, `WORKER_ALLOCATOR_CLASS`, and concrete strategy classes `GreedyAllocator`, `MaxFreeAllocator`, and `RoundRobinAllocator`.

**Control flow:** Setup creates a default `BlockMetadataEvictorView`. Each test sets the allocator class property, calls the factory, and asserts the instance type. The default test leaves original properties and expects `MaxFreeAllocator`.

**State and persistence:** No block state is mutated. It temporarily changes global configuration and reloads properties in `after`.

**Dependencies and integration:** Depends on `Configuration`, `PropertyKey`, `TieredBlockStoreTestUtils.defaultMetadataManagerView`, JUnit rules, and allocator class names.

**Risks:** Factory failures usually appear as reflection or constructor signature issues. Default strategy changes must update this test intentionally.

**Test signals:** Provides direct coverage for configured allocator selection and default policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorTestBase.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorTestBase.java

**Purpose:** Shared fixture and assertion library for allocator strategy tests.

**Important APIs:** Defines default MEM/SSD/HDD tier topology and helpers `before`, `resetManagerView`, `assertTempBlockMeta` overloads, `getMetadataEvictorView`, `assertAllocationAnyDirInTier`, `assertAllocationAnyDirInAnyTierWithMedium`, and `assertAllocationInSpecificDir`.

**Control flow:** Setup disables reviewer rejection through `MockReviewer`, creates a default multi-tier configuration, builds `BlockMetadataManager`, and initializes common `BlockStoreLocation` targets. Assertions request allocations, check presence/absence, validate size and target location, and may add committed blocks to consume capacity.

**State and persistence:** Uses temporary directories and in-memory metadata. Some assertions add `DefaultBlockMeta` to dirs to simulate consumed space.

**Dependencies and integration:** Supports `GreedyAllocatorTest`, `MaxFreeAllocatorTest`, `RoundRobinAllocatorTest`, and contract tests. Depends on tier setup utilities, metadata view, reviewer configuration, storage dir/view APIs, and Alluxio constants.

**Risks:** Shared expected capacities and locations encode allocator assumptions; if tier topology changes, many strategy tests need coordinated updates. It mutates global configuration.

**Test signals:** Provides reusable checks for allocation success/failure, concrete directory choice, medium-aware allocation, and view reset behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/AllocatorTestBase.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/GreedyAllocatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/GreedyAllocatorTest.java

**Purpose:** Tests the placement policy of `GreedyAllocator`, which chooses the first viable directory according to tier/directory scan order.

**Important APIs:** Exercises `GreedyAllocator.allocateBlockWithView` through base assertions and direct allocation scenarios.

**Control flow:** Setup selects `GreedyAllocator` in configuration and creates the allocator from a metadata view; teardown reloads configuration. The main test fills dirs in controlled order and asserts which location is chosen or rejected. Additional tests reuse base assertions for any-dir-in-tier, any-dir-in-any-tier-with-medium, and specific-dir requests.

**State and persistence:** Uses in-memory metadata and committed block additions to consume capacity. No durable data beyond temporary test dirs.

**Dependencies and integration:** Extends `AllocatorTestBase`, uses block store locations, storage dirs/views, and Alluxio configuration.

**Risks:** Greedy policy is sensitive to directory order. Changes in `BlockMetadataEvictorView` ordering can alter placement even if capacity logic remains correct.

**Test signals:** Validates first-fit behavior, capacity rejection, tier/medium-specific constraints, and exact directory targeting for Greedy allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/GreedyAllocatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/MaxFreeAllocatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/MaxFreeAllocatorTest.java

**Purpose:** Tests `MaxFreeAllocator`, the default allocator that chooses the directory with the most available space within the requested location constraints.

**Important APIs:** Exercises `MaxFreeAllocator.allocateBlockWithView` through direct scenarios and base helper assertions.

**Control flow:** Setup sets allocator class to `MaxFreeAllocator`; teardown reloads configuration. Tests allocate under multiple capacity-consumption patterns and verify the chosen directory follows max-free ordering. Base tests cover any-dir-in-tier, medium-aware any-tier, and specific directory behavior.

**State and persistence:** Uses temporary tier directories and metadata view state. Capacity is manipulated by adding committed metadata in helper methods.

**Dependencies and integration:** Extends `AllocatorTestBase` and is tied to the configured default allocator expected by `AllocatorFactoryTest`.

**Risks:** Available-byte calculations must include pinned/locked filtering from the view where applicable. Directory removal or capacity accounting errors can cause suboptimal or invalid choices.

**Test signals:** Covers max-free selection, capacity boundaries, and common allocator contract paths for the default strategy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/MaxFreeAllocatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/RoundRobinAllocatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/RoundRobinAllocatorTest.java

**Purpose:** Tests `RoundRobinAllocator`, which rotates allocation choices across eligible directories while respecting capacity and location constraints.

**Important APIs:** Exercises round-robin allocation through `Allocator.Factory.create`, direct placement assertions, and base helper tests.

**Control flow:** Setup selects `RoundRobinAllocator`; teardown reloads configuration. The main test performs repeated allocations of controlled sizes and validates rotation across dirs/tier targets, behavior after dirs fill, and failure when no eligible location remains. Additional tests reuse base checks for tier wildcard, medium wildcard, and specific-dir allocation.

**State and persistence:** Maintains allocator-internal cursor state plus metadata capacity changes. Temporary directories exist but data is represented mostly through metadata.

**Dependencies and integration:** Extends `AllocatorTestBase`, uses global allocator configuration, storage views, and block store locations.

**Risks:** Cursor state can produce order-dependent failures if not reset between tests or when directory availability changes. Dynamic deletion/fill behavior must not point to removed/full dirs.

**Test signals:** Covers rotation, capacity exhaustion, location filtering, and shared allocator contracts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/allocator/RoundRobinAllocatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/AbstractBlockAnnotatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/AbstractBlockAnnotatorTest.java

**Purpose:** Abstract base tests and helpers for block eviction-order annotators/iterators.

**Important APIs:** Provides `init`, `createBlock`, `moveBlock`, `removeBlock`, `accessBlock`, `getDir`, `validateIterator`, plus common tests `testRemovedBlock` and `testMovedBlock`.

**Control flow:** `init` creates default metadata and obtains the first block iterator event listener. Helpers seed committed blocks, manually update metadata for moves/removals, and notify the listener about commit/move/remove/access events. Common tests verify iterator output before and after remove or move events.

**State and persistence:** Uses temporary tier directories and metadata. Tracks block ID to `StorageDir` in a map to drive event notifications.

**Dependencies and integration:** Used by LRU and LRFU annotator tests. Depends on `BlockIterator`, `BlockStoreEventListener`, `StorageTierAssoc`, and `TieredBlockStoreTestUtils`.

**Risks:** Helpers manually simulate events; if production event order differs, tests may not catch every integration issue. Still, they protect iterator state updates for remove and move.

**Test signals:** Common regression coverage that annotators drop removed blocks and keep moved blocks visible in natural order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/AbstractBlockAnnotatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/EmulatingBlockIteratorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/EmulatingBlockIteratorTest.java

**Purpose:** Tests `EmulatingBlockIterator`, which emulates eviction order from an evictor class such as `LRUEvictor`.

**Important APIs:** Exercises metadata block iterator creation under `WORKER_EVICTOR_CLASS`, event listener callbacks for commit/access, and iterator retrieval by `BlockStoreLocation` and `BlockOrder`.

**Control flow:** Setup enables LRU eviction emulation, creates metadata/iterator/listener, and tracks block locations. The test creates several blocks across dirs, accesses blocks to change recency, and validates that iterator headers match expected LRU-style order.

**State and persistence:** Uses in-memory iterator state plus committed test block metadata/files. A local block-location map supplies event context.

**Dependencies and integration:** Depends on configuration, `LRUEvictor`, `StorageTierAssoc`, `BlockStoreEventListener`, and tiered-store test utilities.

**Risks:** Emulation must stay consistent with the real evictor's ordering semantics. If listener callbacks are missed or location filters are wrong, eviction may choose stale candidates.

**Test signals:** Focused coverage that access events reorder blocks as expected under LRU emulation and that iterator prefixes match expected eviction order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/EmulatingBlockIteratorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRFUAnnotatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRFUAnnotatorTest.java

**Purpose:** Tests `LRFUAnnotator`, the block ordering policy blending recency and frequency.

**Important APIs:** Configures `LRFUAnnotator`, initializes common annotator fixtures, and validates iterator order after create/access operations.

**Control flow:** Setup creates the metadata/iterator through `AbstractBlockAnnotatorTest.init` and selects the LRFU annotator. The test creates blocks, performs access patterns that should change combined recency/frequency scores, then compares iterator output to expected block ID order.

**State and persistence:** Maintains annotator score/order state through block store event listener callbacks and temporary committed block metadata.

**Dependencies and integration:** Extends the abstract annotator test, uses Alluxio configuration, storage dirs, and block iterator APIs consumed by eviction.

**Risks:** LRFU behavior is sensitive to time/score decay parameters; deterministic tests must avoid relying on wall-clock ambiguity. Incorrect score updates affect eviction fairness.

**Test signals:** Confirms basic LRFU ordering and inherits remove/move correctness tests from the base class.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRFUAnnotatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRUAnnotatorTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRUAnnotatorTest.java

**Purpose:** Tests `LRUAnnotator`, the least-recently-used block ordering implementation for eviction iteration.

**Important APIs:** Configures `LRUAnnotator`, uses common block create/access helpers, and validates `BlockIterator` order.

**Control flow:** Setup initializes the abstract annotator fixture with LRU configuration. The test creates blocks, accesses selected blocks, and expects iterator order to place least recently used blocks first.

**State and persistence:** State is maintained in annotator/listener order structures and temporary committed block metadata.

**Dependencies and integration:** Extends `AbstractBlockAnnotatorTest`; integrates with `BlockStoreEventListener`, `BlockIterator`, tiered metadata, and eviction ordering.

**Risks:** Missing access notifications or incorrect order updates can cause hot blocks to be evicted. Tests must keep event sequence deterministic.

**Test signals:** Verifies LRU-specific access ordering and inherits common remove/move iterator tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/annotator/LRUAnnotatorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/AlignTaskTest.java -->
## sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/AlignTaskTest.java

**Purpose:** Tests `AlignTask`, a tier-management task that aligns blocks across tiers according to management policy.

**Important APIs:** Exercises `AlignTask.run` or task execution through `BaseTierManagementTaskTest`, block placement helpers, and tier-alignment configuration.

**Control flow:** Setup calls the base tier-management fixture and creates an `AlignTask` for the test metadata/store context. The test seeds blocks in tiers/dirs, runs the task, and validates that blocks are moved into the expected aligned layout.

**State and persistence:** Uses temporary tiered block store state from the base class, including real local block metadata/files and movement side effects.

**Dependencies and integration:** Depends on tier-management base fixtures, `TieredBlockStore`, allocation/move logic, configuration flags for tier alignment, and block metadata views.

**Risks:** Alignment tasks can conflict with locks, reserved space, and ongoing writes. Incorrect move planning could churn data or violate storage constraints.

**Test signals:** Provides focused coverage that the alignment management task produces expected placement changes under a controlled tier topology.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/AlignTaskTest.java -->
