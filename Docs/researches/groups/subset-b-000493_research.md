# subset-b-000493 research

Grouped research report for the requested Alluxio worker block-management, worker block metadata, worker gRPC/page tests, Guava test helper, and FUSE integration files. Each section is keyed by original source path for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BaseTierManagementTaskTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BaseTierManagementTaskTest.java

Purpose: shared fixture for tier-management background task tests. It creates a deterministic two-tier `TieredBlockStore` layout and exposes selected storage directories for alignment, promotion, and swap/restore tests.

Important APIs and helpers: constants define tier aliases, block sizes, and the synthetic load session/block IDs. `init()` configures the accepting reviewer, LRU annotator, default block size, and load-detection cooldown, then builds the default test tier layout. `startSimulateLoad()` creates a temporary uncommitted block and writer; `stopSimulateLoad()` aborts it and closes the writer.

Control flow and state: `init()` uses `TieredBlockStoreTestUtils.setupDefaultConf`, constructs a real `TieredBlockStore`, then reflects out its private `mMetaManager` to obtain `BlockMetadataManager`, `BlockIterator`, and concrete `StorageDir` objects. The synthetic writer keeps the worker "busy" until tests release it, gating background management tasks.

Dependencies and integration: depends on global `Configuration`, `TieredBlockStore`, `BlockMetadataManager`, `LRUAnnotator`, `AllocateOptions`, and JUnit `TemporaryFolder`.

Risks and test signals: reflection against `mMetaManager` is brittle if internals are renamed. Global configuration mutation requires callers to reload/reset before setup. The fixture strongly signals integration-level task behavior because it uses real block-store metadata rather than mocks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BaseTierManagementTaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BlockTransferPartitionerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BlockTransferPartitionerTest.java

Purpose: verifies `BlockTransferPartitioner.partitionTransfers` groups block moves into parallel partitions without over-splitting transfers that share fully identified source or destination locations.

Important APIs and helpers: `testEmptyList`, `testPartitioning`, `generateTransferLists`, `generateTransfers`, and `validatePartitions`. Test transfer records are built with `BlockTransferInfo.createMove` and either exact `BlockStoreLocation(tier, dir)` values or wildcard `anyDirInTier` values.

Control flow and state: the test generates permutations where source, destination, or both sides are allocated. Location distributions such as `{2,2}`, `{3,1}`, `{1,1,2}`, and `{1,1,1,1}` are fed into the partitioner with requested partition counts from one to four. Assertions check only partition count and sizes, making grouping shape the observable contract.

Dependencies and integration: integrates the management package partitioner with worker block eviction transfer metadata and `BlockStoreLocation` identity semantics.

Risks and test signals: it does not assert transfer ordering or location exclusivity inside each partition, so regressions preserving sizes could pass. It is a focused signal for concurrency throttling and conflict grouping around move planning.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/BlockTransferPartitionerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/PromoteTaskTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/PromoteTaskTest.java

Purpose: integration test for the tier-management promotion task moving blocks from a lower tier into available higher-tier space.

Important APIs and helpers: extends `BaseTierManagementTaskTest`; `before()` reloads configuration, disables tier alignment, sets `WORKER_MANAGEMENT_TIER_PROMOTE_QUOTA_PERCENT`, and calls `init()`. `testBlockPromotion()` uses `TieredBlockStoreTestUtils.cache` and `CommonUtils.waitFor`.

Control flow and state: the test starts simulated load to defer management work, fills lower-tier `mTestDir3` with committed blocks, asserts upper-tier directories are empty, then stops the load. It computes the expected first-tier used-byte limit from tier capacity and the promotion quota, then waits until committed bytes in `mTestDir1` plus `mTestDir2` match that quota.

Dependencies and integration: uses real tiered block-store metadata, global worker management properties, and the background task scheduler/load detector.

Risks and test signals: timing depends on a 60-second wait and background task scheduling. It validates byte-level promotion quota behavior, but not which specific blocks were promoted or ordering under LRU.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/PromoteTaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/SwapRestoreTaskTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/SwapRestoreTaskTest.java

Purpose: exercises tier-alignment recovery when swaps can exhaust reserved space and require the swap-restore path.

Important APIs and helpers: extends `BaseTierManagementTaskTest`; setup disables promotion, reserves one `BLOCK_SIZE` for alignment, and uses LRU. `testTierAlignment()` fills one upper-tier directory with small blocks and the remaining directories with large blocks, then uses random access to disturb ordering.

Control flow and state: simulated load blocks background activity while directories are populated and accessed. The test first asserts the `BlockIterator` reports tiers are not naturally aligned from first to second tier. After stopping load, it waits until alignment becomes true for all candidate blocks.

Dependencies and integration: uses `BlockStoreLocation`, `BlockOrder.NATURAL`, `StorageDir`, `TieredBlockStoreTestUtils`, `CommonUtils.waitFor`, and background management tasks.

Risks and test signals: random access is intended to make misalignment likely but not mathematically deterministic. A TODO notes the test does not directly prove the swap-restore task was activated. The pass condition still signals end-to-end realignment under constrained swap space.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/management/tier/SwapRestoreTaskTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultBlockMetaTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultBlockMetaTest.java

Purpose: unit tests for `DefaultBlockMeta` path and committed-size behavior.

Important APIs and helpers: setup creates a temporary storage tier and directory through `DefaultStorageTier.newStorageTier`, then constructs a `DefaultTempBlockMeta` and its committed `DefaultBlockMeta`. Tests cover `BlockMeta.getBlockSize()` and `BlockMeta.getPath()`.

Control flow and state: `getBlockSize()` observes the block size through the file at the commit path. With no file content it reports zero; with a short file it reports the actual short length; with a full file it reports the configured target block size. `getPath()` verifies path construction from the block directory and block ID.

Dependencies and integration: depends on `BufferUtils`, `PathUtils`, `TemporaryFolder`, storage-tier/directory metadata, and local filesystem writes.

Risks and test signals: it exercises filesystem-backed size discovery rather than pure metadata only. Coverage is narrow but important for commit-path compatibility and partial-file size reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultBlockMetaTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageDirTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageDirTest.java

Purpose: broad unit coverage for `DefaultStorageDir` initialization, committed/temp block accounting, capacity checks, cleanup, and location conversion.

Important APIs and helpers: setup builds a `DefaultStorageTier`, directory, block meta, and temp block meta. Helpers create block files, assert empty metadata, and verify cleaned storage directories. Tests cover initialization from existing files, inappropriate file/dir deletion, oversized block rejection, byte counters, getters, block/temp metadata add/remove/get, temp resizing, session cleanup, and `toBlockStoreLocation()`.

Control flow and state: initialization scans real directory contents and reconstructs committed block metadata when file sizes fit capacity. Runtime tests mutate in-memory maps for committed blocks and temp blocks, assert available/committed byte transitions, enforce duplicate and no-space exceptions, and remove only temp blocks belonging to a cleanup session.

Dependencies and integration: depends on `DefaultStorageTier`, `DefaultBlockMeta`, `DefaultTempBlockMeta`, `BlockStoreLocation`, `ExceptionMessage`, Guava `Sets`, `BufferUtils`, and filesystem temp directories.

Risks and test signals: strong signal for storage directory invariants and failure messages, but tests rely on exact global constants and exception text. Concurrency is not covered; behavior is single-threaded metadata mutation plus filesystem initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageDirTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageTierTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageTierTest.java

Purpose: tests `DefaultStorageTier` aggregation of storage directories and tolerance of directory setup failures or misconfiguration.

Important APIs and helpers: setup creates a tier with two temp directories and capacities. Tests cover `getTierAlias`, `getTierOrdinal`, `getCapacityBytes`, `getAvailableBytes`, `getDir`, `getStorageDirs`, tolerant failed directory initialization, tolerant capacity/path misconfiguration, and `removeStorageDir`.

Control flow and state: the tests add block metadata to one directory to observe tier-level available-capacity aggregation. Failure-tolerance cases manipulate config or directory state and verify the tier keeps only usable directories where appropriate. `removeDir` mutates the tier directory list and rejects removing a directory from another tier.

Dependencies and integration: uses `ConfigurationRule`, `TemporaryFolder`, `DefaultStorageTier`, `StorageDir`, and ImmutableList expectations.

Risks and test signals: `getDir(2)` expects `null` despite comments mentioning an exception, which documents current behavior. These tests are useful for startup robustness and tier summary metrics, not for block-store allocation policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultStorageTierTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultTempBlockMetaTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultTempBlockMetaTest.java

Purpose: unit tests for `DefaultTempBlockMeta` path derivation, session ownership, and mutable size.

Important APIs and helpers: setup creates a temporary storage tier/directory and a `DefaultTempBlockMeta`. Tests cover `getPath`, `getCommitPath`, `getSessionId`, and `setBlockSize`.

Control flow and state: path tests assert temp block files live under a per-session temporary path while commit paths resolve to the final block path. The size test confirms the metadata starts at the configured size and can be set to smaller or larger values.

Dependencies and integration: depends on `DefaultStorageTier`, `StorageDir`, `PathUtils`, and JUnit temp directories.

Risks and test signals: narrow coverage documents file naming conventions needed by writers and commit flows. It does not validate storage-dir byte accounting; that is covered by `DefaultStorageDirTest`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/DefaultTempBlockMetaTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageDirViewTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageDirViewTest.java

Purpose: validates `StorageDirEvictorView` as an eviction-facing wrapper over a real storage directory.

Important APIs and helpers: setup builds default metadata, obtains a tier and directory, then wraps them in `BlockMetadataEvictorView`, `StorageTierEvictorView`, and `StorageDirEvictorView`. Tests cover parent view, available/committed/capacity bytes, dir index, medium type, location conversion, evictable block filtering, and temp block creation.

Control flow and state: `getEvictableBlocks()` starts empty, adds a committed block, then checks bytes and block listing. It changes view state through pinned/in-use block tracking in the metadata view and verifies evictable blocks disappear and reappear accordingly.

Dependencies and integration: depends on metadata manager test utilities, `DefaultBlockMeta`, `DefaultTempBlockMeta`, Hamcrest matchers, and `BlockStoreLocation`.

Risks and test signals: strong signal that eviction views respect pinned/in-use state and delegate storage metrics correctly. It does not exercise actual eviction execution or concurrent pin changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageDirViewTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageTierViewTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageTierViewTest.java

Purpose: tests `StorageTierEvictorView` directory-view accessors and metadata-view linkage.

Important APIs and helpers: setup creates default block metadata, selects a storage tier, wraps it in `BlockMetadataEvictorView`, and obtains a `StorageTierEvictorView`. Tests cover `getDirViews`, `getDirView`, bad-index handling, tier alias, tier ordinal, and `getBlockMetadataEvictorView`.

Control flow and state: the view is initialized once from real test metadata. Assertions compare view values back to underlying `StorageTier` properties and expected default layout directory count.

Dependencies and integration: depends on `TieredBlockStoreTestUtils.defaultMetadataManager`, `TemporaryFolder`, and Alluxio storage metadata view classes.

Risks and test signals: coverage is accessor-focused and documents bad directory index behavior returning `null`. It provides support-level signal for eviction-policy code that consumes tier views.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/meta/StorageTierViewTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/MockReviewer.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/MockReviewer.java

Purpose: test-only `Reviewer` implementation that deterministically rejects allocation into directories with selected available-byte values.

Important APIs and helpers: `resetBytesToReject(Set<Long>)` replaces the static rejection set. `acceptAllocation(StorageDirView)` reads `dirView.getAvailableBytes()` and returns false when that value is present in the set.

Control flow and state: all instances share the static `BYTES_TO_REJECT` set. Tests can reconfigure rejection criteria before exercising allocation decisions without needing random probability or real disk pressure.

Dependencies and integration: implements `Reviewer`, consumes `StorageDirView`, and uses Guava `Sets` for the mutable static set.

Risks and test signals: static mutable state must be reset between tests to avoid leakage. It is useful for deterministic allocator/reviewer integration tests, but it is not a production reviewer and has no persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/MockReviewer.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewerTest.java

Purpose: verifies the probability curve used by `ProbabilisticBufferReviewer` as available bytes fall between soft and hard limits.

Important APIs and helpers: setup configures `WORKER_REVIEWER_CLASS`, hard limit, and soft limit, then obtains the reviewer through `Reviewer.Factory.create()`. `testProbabilityFunction()` calls `getProbability(StorageDirView)` on mocked directory views.

Control flow and state: cases cover empty disk, above soft limit, just below soft limit, midpoint between hard and soft, exactly at hard limit, below hard limit, and full disk. Assertions check 1.0, linearly reduced values, and 0.0.

Dependencies and integration: depends on global `Configuration`, `FormatUtils.parseSpaceSize`, Mockito `StorageDirView` mocks, and reviewer factory behavior.

Risks and test signals: global configuration is reset in `@After`. Random acceptance is not tested; this isolates the deterministic probability function and factory wiring for buffer preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ProbabilisticBufferReviewerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ReviewerFactoryTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ReviewerFactoryTest.java

Purpose: validates `Reviewer.Factory.create()` instantiates the configured reviewer class and the default reviewer.

Important APIs and helpers: `createProbabilisticBufferReviewer()` sets `WORKER_REVIEWER_CLASS` to `ProbabilisticBufferReviewer`. `createDefaultAllocator()` calls the factory without local setup and expects the default reviewer type.

Control flow and state: both tests assert the returned `Reviewer` is an instance of `ProbabilisticBufferReviewer`.

Dependencies and integration: uses Alluxio global `Configuration`, `PropertyKey.WORKER_REVIEWER_CLASS`, and JUnit assertions.

Risks and test signals: naming still says allocator in places, but the signal is reviewer factory behavior. The tests do not cover invalid class names or custom reviewer constructors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/reviewer/ReviewerFactoryTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/stream/BlockWorkerDataReaderTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/stream/BlockWorkerDataReaderTest.java

Purpose: integration-style unit tests for client-side `BlockWorkerDataReader` backed by a local `DefaultBlockWorker`, including local-block reads and UFS fallback reads.

Important APIs and helpers: setup builds a one-tier worker store, mocked block/master/session clients, a real local UFS manager, and `BlockWorkerDataReader.Factory`. Tests cover missing-block create failures, reader creation at an offset, repeated create/close for lock release, UFS chunk reads, full local file reads, and partial reads.

Control flow and state: local tests create and commit blocks through `mBlockWorker`, append increasing-byte buffers through `BlockWriter`, then read chunks and validate position. UFS tests write a real temp file, construct persisted `URIStatus`/`FileBlockInfo`, use `ReadPType.NO_CACHE`, and read through `Paged`/worker UFS path.

Dependencies and integration: depends on worker block store, `MonoBlockStore`, `TieredBlockStore`, `UnderFileSystem`, `InStreamOptions`, `FileSystemContext`, and `BufferUtils`.

Risks and test signals: strong signal for reader lifecycle, chunk sizing, offsets, and lock churn. It depends on global modifiable configuration and real temp filesystem behavior, but not a live master.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/block/stream/BlockWorkerDataReaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/AbstractWriteHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/AbstractWriteHandlerTest.java

Purpose: abstract test suite for gRPC write handlers that share the `AbstractWriteHandler` stream protocol.

Important APIs and helpers: concrete subclasses provide `getWriteRequestType()` and `getWriteDataStream()`. Shared tests cover empty file writes, non-empty chunked writes, cancellation, cancellation error suppression, invalid first/later offsets, raw errors, and errors after completion. Helpers build command/data `WriteRequest`s, create test data buffers, capture response errors, and verify written checksums.

Control flow and state: tests send an initial command with offset zero, stream data chunks, then complete/cancel/error the handler. Response observer hooks record completion, errors, and responses using a lock for wait coordination. `checkWriteData` reads back the concrete sink and verifies Adler32 checksum and size.

Dependencies and integration: depends on gRPC `StreamObserver`, `StatusException`, Alluxio `WriteRequest`/`WriteResponse`, `Protocol.WriteRequestCommand`, Netty-backed data buffers, and Mockito.

Risks and test signals: subclasses inherit protocol assertions, so failures identify common write-state machine regressions. It deliberately documents that cancellation does not fully abort files; clients issue separate aborts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/AbstractWriteHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockReadHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockReadHandlerTest.java

Purpose: tests server-side `BlockReadHandler` streaming data from a block reader to gRPC responses.

Important APIs and helpers: setup writes a temp test file, creates a `LocalFileBlockReader`, mocks a ready `ServerCallStreamObserver`, and stubs `BlockWorker.createBlockReader`. Tests cover full reads, partial reads, empty-file error, cancellation after request, raw errors, error after request, and read failure after closing the block reader.

Control flow and state: read requests specify offset and length. The handler emits `ReadResponse` chunks that are collected by the observer; helper logic reconstructs checksums and total bytes. Error assertions capture `StatusException` codes.

Dependencies and integration: depends on gRPC server-call observer backpressure readiness, Alluxio `BlockWorker`, `LocalFileBlockReader`, `ReadRequest`/`ReadResponse`, `Protocol.OpenUfsBlockOptions`, and temp filesystem data.

Risks and test signals: validates chunk streaming and error mapping, but uses a local file reader and mocked worker rather than a full block store. Backpressure is simplified by always returning ready.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockReadHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockWriteHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockWriteHandlerTest.java

Purpose: concrete `AbstractWriteHandlerTest` implementation for writing temporary worker blocks through `BlockWriteHandler`.

Important APIs and helpers: setup creates a `BlockWorker` mock whose `createBlockWriter` returns a `LocalFileBlockWriter` over a temp file, then instantiates `BlockWriteHandler`. It overrides request type to `ALLUXIO_BLOCK` and reads written data from the temp file.

Control flow and state: inherited tests exercise the write protocol. Additional tests close the writer before a data chunk to force write failure, and assert `getLocation()` begins with the temp-block location prefix after initialization.

Dependencies and integration: depends on `LocalFileBlockWriter`, `BlockWorker`, gRPC write request types, and the abstract suite.

Risks and test signals: focused on handler/file-writer integration and status-code behavior. It uses mocks for block-worker side effects, so commit/abort semantics are covered elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/BlockWriteHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/GrpcExecutorsTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/GrpcExecutorsTest.java

Purpose: verifies worker gRPC executor wrappers propagate authenticated client user context into worker threads.

Important APIs and helpers: setup and teardown manipulate `AuthenticatedClientUser`. `validateAuthenticatedClientUser(ExecutorService)` submits tasks under two different context users and asserts `AuthenticatedClientUser.getClientUser()` inside the executor matches the caller context.

Control flow and state: each test obtains an executor from `GrpcExecutors` for block reader, block writer, or async cache manager work. The caller context is changed between submissions to ensure wrapping is per-task rather than a stale thread-local value.

Dependencies and integration: depends on `GrpcExecutors`, `AuthenticatedClientUser`, `AuthenticatedUserInfo`, and Java `ExecutorService`.

Risks and test signals: strong signal for security/impersonation context propagation. It does not validate executor sizing, shutdown, or exception handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/GrpcExecutorsTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockReadHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockReadHandlerTest.java

Purpose: tests `ShortCircuitBlockReadHandler` opening local block paths for clients, including promotion and pinning behavior.

Important APIs and helpers: setup creates a real `TieredBlockStore` with two temp tiers, mocked block-master client pool, and a custom response observer. Tests cover nonexistent block access, access without promotion, access with promotion, pinning while open, unpin on error, and rejecting repeated access on the same handler.

Control flow and state: helper `createLocalBlock` creates, writes, and commits a block in a selected tier. `accessBlock` sends `OpenLocalBlockRequest`, completes the stream, and asserts one response with the expected local path. Promotion changes expected location from second tier to first tier.

Dependencies and integration: depends on `ShortCircuitBlockReadHandler`, `TieredBlockStore`, `BlockWriter`, worker tier configuration, `OpenLocalBlockRequest/Response`, and Mockito.

Risks and test signals: strong signal for local-read lifecycle, pin/unpin correctness, and promotion integration. It uses timeouts for error paths and local filesystem state, so slow cleanup could cause flakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockReadHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandlerTest.java

Purpose: tests `ShortCircuitBlockWriteHandler` creating local temp block files and handling abort/commit lifecycle through direct path responses.

Important APIs and helpers: setup creates a temp directory, `CreateLocalBlockRequest`, handler, response observer, and in-file `TestBlockWorker`. Tests cover normal create/commit, a second request before commit aborting prior state, reserving space before creation, cancellation abort, and error abort.

Control flow and state: the first `onNext` creates a local temp file and responds with a path while leaving the stream open. `onCompleted` commits; `onError` and cancellation cleanup temp state. `TestBlockWorker` tracks temp and committed block sets, writes files, implements `requestSpace`, and cleans session state.

Dependencies and integration: depends on `CreateLocalBlockRequest/Response`, `NoopBlockWorker`, `CreateBlockOptions`, local filesystem, and a custom observer.

Risks and test signals: very useful lifecycle signal without a full real worker. The fake worker is not thread-safe and simplifies capacity/accounting, so concurrent behavior and real allocator failures are outside scope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/ShortCircuitBlockWriteHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandlerTest.java

Purpose: concrete write-handler tests for fallback from a partially written local block to a UFS block file.

Important APIs and helpers: setup builds a real `MonoBlockStore`/`TieredBlockStore`, mocked `BlockWorker`, mocked `UnderFileSystem`, and an output stream. It pre-creates a partial local temp block of `PARTIAL_WRITTEN` bytes. Helpers create fallback init requests containing `CreateUfsBlockOptions`.

Control flow and state: `noTempBlockFound` removes the partial block before fallback and expects an error. `tempBlockWritten` starts fallback at the partial length, streams more data, completes, and verifies the combined output through the inherited checksum helper. `getLocation` asserts UFS block paths start under `/.alluxio_ufs_blocks`.

Dependencies and integration: depends on `UfsFallbackBlockWriteHandler`, `UfsManager`, `UnderFileSystem`, `MonoBlockStore`, block master worker ID, and abstract write-handler behavior.

Risks and test signals: strong for hybrid local/UFS recovery and offsets. It uses mocked UFS create behavior and a local in-memory stream, not a real remote object store.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFallbackBlockWriteHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFileWriteHandlerTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFileWriteHandlerTest.java

Purpose: concrete `AbstractWriteHandlerTest` implementation for direct UFS file writes.

Important APIs and helpers: setup mocks `UfsManager`, `UfsClient`, and `UnderFileSystem.createNonexistingFile` to return a `ByteArrayOutputStream`, then constructs `UfsFileWriteHandler`. It overrides command construction with `CreateUfsFileOptions` and request type `UFS_FILE`.

Control flow and state: inherited tests stream data and verify the byte array output. `writeFailure` closes the output stream between chunks to trigger handler error behavior. `getLocation` verifies the handler reports the target UFS path.

Dependencies and integration: depends on UFS manager APIs, `Protocol.CreateUfsFileOptions`, gRPC write protocol, and abstract write-handler tests.

Risks and test signals: validates stream protocol and UFS path plumbing but not actual remote filesystem semantics. The mock output stream makes failure injection deterministic.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/grpc/UfsFileWriteHandlerTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageEvictorTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageEvictorTest.java

Purpose: randomized differential test for `BlockPageEvictor`, ensuring block pinning wraps underlying page evictors correctly.

Important APIs and helpers: parameterized data combines `LRUCacheEvictor`, `LFUCacheEvictor`, and `FIFOCacheEvictor` with block/page/pinned-block counts. `runAndInspect` applies random get/put/delete access sequences to both the wrapped evictor and a truth supplier. `pinnedBlocks` uses `addPinnedBlock` and `removePinnedBlock`.

Control flow and state: for each parameter set, a fixed-seed random stream produces many page operations. Without pins, wrapped eviction should match inner eviction. With pins, eviction is compared against `inner.evictMatching` excluding pinned block IDs, then pins are removed and normal behavior resumes.

Dependencies and integration: depends on Alluxio cache evictors, `PageId`, `BlockPageEvictor`, and reflection utility construction.

Risks and test signals: randomized but deterministic by seed; strong signal across eviction algorithms. It checks selected eviction result, not full internal queues.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageEvictorTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageIdTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageIdTest.java

Purpose: tests identity, hashing, parsing, and downcast behavior for `BlockPageId`.

Important APIs and helpers: tests cover constructors from numeric and string file IDs, equality with parent `PageId`, set-key behavior, inequality with another subclass, hash-code consistency, `getBlockId`, `getBlockSize`, `downcast`, and malformed file IDs. `MoreFieldsPageId` models a conflicting subclass.

Control flow and state: valid file IDs use the `paged_block_<hex>_size_<hex>` encoding, including a negative block ID represented as all hex f's. Invalid cases cover bad prefix, insufficient digits, empty ID, extra suffix, and negative block size.

Dependencies and integration: depends on Alluxio cache `PageId`, Guava collection helpers, and JUnit exception assertions.

Risks and test signals: strong compatibility signal for file ID encoding used by paged block store metadata. It intentionally verifies cross-class equality with raw `PageId`, which is important for map/set lookups.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/BlockPageIdTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/ByteArrayCacheManager.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/ByteArrayCacheManager.java

Purpose: test-only in-memory `CacheManager` storing pages as byte arrays for paged block reader tests.

Important APIs and helpers: `put` copies a `ByteBuffer` into a map and increments `mPagesCached`; `get` writes cached bytes into a `ReadTargetBuffer` and increments `mPagesServed`; `getAndLoad` reads from cache or calls an external supplier and caches the result. It also supports `delete`, `deleteFile`, `deleteTempFile`, `getUsage`, `state`, and `close`.

Control flow and state: page contents are held in `Map<PageId, byte[]>`. Missing pages return zero bytes; loaded pages are cached before returning. `Usage` reports used bytes from page lengths and unbounded integer capacity/availability.

Dependencies and integration: implements `alluxio.client.file.cache.CacheManager`, uses `CacheContext`, `ReadTargetBuffer`, `PageId`, and optional `CacheUsage`.

Risks and test signals: not thread-safe and does not implement append or file commit. It provides deterministic cache-hit/cache-miss behavior for reader tests without local page-store side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/ByteArrayCacheManager.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockMetaStoreTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockMetaStoreTest.java

Purpose: tests `PagedBlockMetaStore` block/page bookkeeping, reset, listeners, sticky allocation, and allocation side effects.

Important APIs and helpers: setup builds worker page-store dirs from `CacheManagerOptions`. Tests cover adding pages to blocks across dirs, removing last pages and blocks, reset, remove listeners, sticky allocation for existing block file IDs, and ensuring `allocate` alone does not add files or blocks. `RandomAllocator` supplies non-deterministic backing allocation.

Control flow and state: pages are added through `addBlock` and `addPage`, then store metadata and per-dir cached page counters are asserted. Removing all pages for a block deletes block metadata and triggers listeners. Sticky allocation records the directory once a block exists, then repeated allocations for that file ID return the same dir.

Dependencies and integration: depends on `PagedBlockStoreDir`, `PagedBlockMeta`, `PagedBlockStoreMeta`, `PageInfo`, `Allocator`, and worker page-store configuration.

Risks and test signals: strong signal for metadata consistency and listener behavior. It does not validate persisted page bytes, only metadata-level page accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockMetaStoreTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockReaderTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockReaderTest.java

Purpose: parameterized tests for `PagedBlockReader` reading block bytes through a cache manager and UFS-backed page reader.

Important APIs and helpers: parameters vary page size, buffer size, and block offset. Setup creates a temp UFS block with increasing bytes, mounts it in `UfsManager`, creates `PagedUfsBlockReader`, `PagedBlockMeta`, and `PagedBlockReader` with `ByteArrayCacheManager`. Tests cover one-shot sequential read, multi-round sequential reads, random reads to EOF, random jumping reads, and `transferTo`.

Control flow and state: reads request byte ranges from the block. The reader fetches pages through the cache manager, which loads from UFS on miss. Assertions validate returned `ByteBuffer`/Netty buffer contents against increasing-byte patterns and EOF behavior after full transfer.

Dependencies and integration: depends on page-store options, UFS block read options, `UfsInputStreamCache`, `ByteArrayCacheManager`, Netty `ByteBuf`, and local filesystem UFS.

Risks and test signals: strong for page-boundary and offset math. It avoids real local cache persistence by using in-memory cache, so page-store crash recovery is out of scope.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockReaderTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreCommitBlockTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreCommitBlockTest.java

Purpose: tests `PagedBlockStore.commitBlock` event ordering and failure behavior for local metadata commit and master commit.

Important APIs and helpers: setup constructs a local page-store dir, mocked `BlockMasterClientPool`/`BlockMasterClient`, `PagedBlockStoreDir`, and a spied `BlockStoreEventListener`. `prepareBlockStore()` allocates a temp block, creates a block writer, waits for cache manager read-write state, appends data, and registers the listener.

Control flow and state: success test commits locally and to master and verifies both listener callbacks. One test overrides `PagedBlockMetaStore.commit` to throw and expects no local or master callbacks. Another makes `BlockMasterClient.commitBlock` throw `UNAVAILABLE`; local callback fires but master callback does not.

Dependencies and integration: depends on `PagedBlockStore`, `CacheManager.Factory`, page-store dirs, mocked block master RPC, `CreateBlockOptions`, and event listener contracts.

Risks and test signals: good signal for partial failure boundaries and listener notification sequencing. It uses a real local page store but mocks master RPC and worker ID.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreCommitBlockTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreDirTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreDirTest.java

Purpose: tests `PagedBlockStoreDir` wrapping of a `PageStoreDir` for block-aware counters, eviction, temp pages, commit, and abort.

Important APIs and helpers: setup creates a local page-store dir with FIFO eviction. Tests cover root path, dir index, `BlockStoreLocation`, number of blocks, cached bytes, page put idempotence, page delete idempotence, evictor updates, temp-page add/commit, and temp-page abort.

Control flow and state: committed page operations update per-block page counts and byte counts. Temp page operations record temp file IDs without counting committed blocks until `commit(fileId)`, while `abort(fileId)` clears temp state and page-store temporary data.

Dependencies and integration: depends on `LocalPageStoreDir`, `PageStoreOptions`, `PageInfo`, `BlockPageId`, `BlockPageEvictor`, and `PagedBlockStoreMeta` default tier/medium constants.

Risks and test signals: strong signal for dir-local accounting and temp-to-committed transitions. It does not cover multi-dir allocation or disk-full errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreDirTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreMetaTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreMetaTest.java

Purpose: tests `PagedBlockStoreMeta` aggregate reporting produced from `PagedBlockMetaStore`.

Important APIs and helpers: setup configures two memory page-store directories with capacities and paths. `generatePages` creates block metadata and page metadata in a selected dir. Tests cover full block lists, no-detailed block list mode, capacity totals by tier/dir, directory paths, lost storage, used bytes, and storage tier association.

Control flow and state: pages are generated across dirs, then `getStoreMetaFull()` or `getStoreMeta()` is inspected. Detailed mode returns block lists by tier and by `BlockStoreLocation`; summary mode omits those maps but keeps counts/capacity/usage.

Dependencies and integration: depends on `CacheManagerOptions`, `PageStoreDir`, `PageInfo`, `BlockPageId`, `PagedBlockMeta`, `BlockStoreLocation`, and default paged-store tier constants.

Risks and test signals: good signal for worker storage metrics exposed to masters/clients. It assumes specific configured page-store paths and default tier/medium names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockStoreMetaTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockWriterTest.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockWriterTest.java

Purpose: parameterized tests for `PagedBlockWriter` appending bytes into temporary page-cache files and preserving data across page boundaries.

Important APIs and helpers: setup configures page size, creates a local page store, FIFO evictor, `DefaultPageMetaStore`, `LocalCacheManager`, waits for read-write state, and constructs a writer. Tests cover appending Netty `ByteBuf` and Java `ByteBuffer` inputs for several page sizes.

Control flow and state: each test appends a series of increasing-byte chunks, closes the writer, commits the temp file ID to final block file ID in both page metadata and page-store dir, then reads cached pages back through the cache manager and validates byte patterns.

Dependencies and integration: depends on `LocalCacheManager`, `PageStore`, `LocalPageStoreDir`, `BlockPageId`, `CacheContext`, `ByteArrayTargetBuffer`, and worker page-store configuration.

Risks and test signals: strong for write chunking, temp-file commit naming, and cache readback. It does not exercise `PagedBlockStore` commit-to-master behavior or cache eviction while writing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/alluxio/worker/page/PagedBlockWriterTest.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/com/google/common/util/concurrent/MockRateLimiter.java -->
# sources/distributed-fs/alluxio/core/server/worker/src/test/java/com/google/common/util/concurrent/MockRateLimiter.java

Purpose: Guava-package test helper that provides a deterministic `RateLimiter` with a fake clock and observable sleep events.

Important APIs and helpers: constructor creates `RateLimiter.create(permitsPerSecond, mTicker)`. `getGuavaRateLimiter()` exposes the real Guava limiter. `sleepMillis(int)` advances user time. `readEventsAndClear()` returns and clears recorded events. Nested `FakeSleepingTicker` extends `RateLimiter.SleepingStopwatch`.

Control flow and state: `readMicros()` returns fake time. User sleeps record `U<seconds>` events; rate-limiter sleeps record `R<seconds>` events through `sleepMicrosUninterruptibly`. Each sleep advances the fake microsecond counter.

Dependencies and integration: intentionally lives in `com.google.common.util.concurrent` because older Guava made `SleepingStopwatch` package-private. Uses `MILLISECONDS`, `Locale.ROOT`, and event lists.

Risks and test signals: package placement couples tests to Guava internals and version behavior. It is useful for deterministic throttling tests without wall-clock sleeps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/core/server/worker/src/test/java/com/google/common/util/concurrent/MockRateLimiter.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse -->
# sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse

Purpose: operational shell entrypoint for mounting, unmounting, and listing Alluxio FUSE mounts.

Important APIs and helpers: `get_env` sources Alluxio config and builds the shaded FUSE jar classpath. `check_fuse_jar` validates packaging. `mount_fuse` resolves mount point/alluxio path defaults, optionally starts StackFS, foreground mode, or background AlluxioFuse. `kill_process_and_umount_fuse`, `umount_fuse`, `fuse_stat`, and `fuse_mounted` manage process and mount state.

Control flow and state: `main` parses `mount`, `umount|unmount`, and `stat`. Mount first tries to kill/unmount existing mount state, builds Java command strings from global shell variables/options, then either `exec`s foreground or `nohup`s background and checks the PID after a sleep. Unmount finds a PID from `fuse_stat`, optionally sends SIGKILL, otherwise waits for graceful exit and mount disappearance.

Dependencies and integration: depends on `alluxio-config.sh`, `${BIN}/alluxio getConf`, Java, shaded `alluxio-integration-fuse` jar, `umount`, `fusermount`, `mount`, `ps`, `grep`, `awk`, and AlluxioFuse/StackMain classes.

Risks and test signals: argument handling and command construction are shell-string based, so paths/options with spaces are risky. There is a bug-like check `[[ check_fuse_jar == 1 ]]` that compares literal text instead of calling the function. Process parsing assumes command layout and may match multiple PIDs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse-sdk -->
# sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse-sdk

Purpose: SDK-oriented shell entrypoint for mounting arbitrary UFS addresses through Alluxio FUSE without requiring an Alluxio namespace path.

Important APIs and helpers: `mount_command` separates JVM options from class arguments; `launch_fuse_process` parses mount options and foreground mode; `wait_for_fuse_mounted` polls `mount`; `print_mount_status` lists running AlluxioFuse mounts; `unmount_command`, `umount_fuse`, and `wait_for_fuse_process_killed` manage shutdown; `check_fuse_jar` validates the shaded jar.

Control flow and state: `main` dispatches `mount`, `umount|unmount`, and help. Mount requires `ufs_address` and `mount_point`, aggregates repeated `-o` options, refuses already-mounted targets, builds a Java command invoking `alluxio.fuse.AlluxioFuse -m <mount> -u <ufs>`, and either execs foreground or starts background and waits up to about a minute for the mount to appear.

Dependencies and integration: depends on Alluxio libexec configuration, Java, shaded FUSE jar, AlluxioFuse class, OS `mount`, `umount`, `fusermount`, `ps`, `grep`, `awk`, and logs under `ALLUXIO_LOGS_DIR`.

Risks and test signals: shell parsing of process command lines and unquoted command execution can break for spaces/special characters. `umount_fuse` calls `fuse_mounted` without passing `mount_point` in its final check, which can mask state. It has no unit tests in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/bin/alluxio-fuse-sdk -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/pom.xml -->
# sources/distributed-fs/alluxio/integration/fuse/pom.xml

Purpose: Maven module descriptor for the Alluxio FUSE integration artifact and shaded runnable jar.

Important APIs and helpers: declares parent `alluxio-integration`, artifact `alluxio-integration-fuse`, module name/description, build path property, dependencies, and a `maven-shade-plugin` execution named `uber-jar`.

Control flow and state: during `package`, the shade plugin builds `${project.artifactId}-${project.version}-jar-with-dependencies`, merges service resources, Apache license/notice resources, and filters signature/license files. Runtime dependencies include `jnr-fuse`, Guava, commons-cli, server common, fs client, core common, jnifuse fs, and Jersey. Test dependencies include core-common test jar and local/S3A underfs modules.

Dependencies and integration: this POM is what the FUSE launcher scripts expect at `target/alluxio-integration-fuse-${VERSION}-jar-with-dependencies.jar`.

Risks and test signals: packaging is sensitive to shaded dependency services and jar naming; launcher scripts fail if this exact output is absent. The filter artifact pattern contains a trailing space in `*:* `, which is suspicious and could affect matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/pom.xml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseCommand.java

Purpose: command interface for FUSE special commands exposed through synthetic Alluxio CLI paths.

Important APIs and helpers: extends the general `Command` interface and adds default `validateArgs(String[])` and `run(AlluxioURI, String[])` methods. The default validator is a no-op; the default runner returns `null`.

Control flow and state: concrete commands override validation and run behavior as needed. The interface itself has no mutable state or persistence.

Dependencies and integration: depends on `AlluxioURI`, `URIStatus`, and `InvalidArgumentException`. It is consumed by `FuseShell` and command implementations under `alluxio.cli.command`.

Risks and test signals: default `run` returning null can hide incomplete command implementations until runtime. There are no direct tests here; behavior is validated through concrete command and shell tests elsewhere.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseShell.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseShell.java

Purpose: dispatcher for FUSE special commands encoded in path suffixes such as `.alluxiocli.metadatacache.size`.

Important APIs and helpers: constructor loads commands from the package using `CommandUtils.loadCommands`. `isSpecialCommand(AlluxioURI)` detects paths whose last segment starts with `Constants.ALLUXIO_CLI_PATH`. `runCommand(AlluxioURI)` parses command tokens, walks subcommands, validates arguments, executes the selected `FuseCommand`, and returns a mock `URIStatus`.

Control flow and state: `runCommand` uses the parent URI as the command target path and splits suffix tokens on dots. It logs usage and throws `InvalidArgumentRuntimeException` for missing, unknown, or invalid commands. For nested commands, it repeatedly descends through `Command.getSubCommands()`.

Dependencies and integration: depends on Alluxio file system, configuration, command loading, constants, logging, and metadata-cache commands.

Risks and test signals: dot-separated path parsing means command names/arguments cannot contain dots without ambiguity. Errors are logged rather than returned as normal status. No direct tests are in this subset.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/FuseShell.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/AbstractFuseShellCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/AbstractFuseShellCommand.java

Purpose: base class for FUSE shell commands, storing common filesystem/configuration context and parent command name.

Important APIs and helpers: constructor accepts `FileSystem`, `AlluxioConfiguration`, and parent command name. `getParentCommandName()` exposes the parent name for usage strings. Fields are protected and final.

Control flow and state: no command execution occurs here; subclasses inherit the stored dependencies and implement `Command`/`FuseCommand` methods. The class is annotated `@ThreadSafe` because state is immutable after construction.

Dependencies and integration: implements `FuseCommand` and depends on Alluxio `FileSystem` and configuration.

Risks and test signals: as a thin base class, risk is mainly constructor contract consistency. No direct tests are present, but all concrete FUSE commands depend on its context wiring.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/AbstractFuseShellCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/MetadataCacheCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/MetadataCacheCommand.java

Purpose: top-level FUSE special command for inspecting or mutating the client metadata cache.

Important APIs and helpers: static `SUB_COMMANDS` maps `dropAll`, `drop`, and `size` to constructors. Constructor instantiates subcommands with the same `FileSystem`, configuration, and parent command name. Overrides `getSubCommands`, `getCommandName`, `getUsage`, and `getDescription`.

Control flow and state: command execution is delegated entirely to subcommands by `FuseShell`. Usage is generated as a synthetic `ls -l` path under default FUSE mount and `.alluxiocli.metadatacache.(...)`.

Dependencies and integration: depends on `DropAllCommand`, `DropCommand`, `SizeCommand`, `Constants`, and `TwoKeyConcurrentMap.TriFunction` constructor references.

Risks and test signals: subcommand map iteration order is unspecified, so usage command order may vary. The command is thread-safe in annotation, but `HashMap` contents are mutable after construction if exposed through `getSubCommands`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/MetadataCacheCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/AbstractMetadataCacheSubCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/AbstractMetadataCacheSubCommand.java

Purpose: shared implementation for metadata-cache FUSE subcommands, enforcing configuration and locating the correct metadata-caching filesystem wrapper.

Important APIs and helpers: overrides `run(AlluxioURI, String[])` to require `USER_METADATA_CACHE_ENABLED`, then calls abstract `runSubCommand(AlluxioURI, String[], MetadataCachingFileSystem)`. `findMetadataCachingFileSystem()` accepts either direct `MetadataCachingFileSystem` or a `LocalCacheFileSystem` whose underlying filesystem is metadata-caching.

Control flow and state: command execution first checks configuration, then unwraps filesystem layers, throwing runtime/illegal-state errors when metadata cache support is disabled or the filesystem type is unexpected.

Dependencies and integration: depends on `MetadataCachingFileSystem`, `LocalCacheFileSystem`, `PropertyKey.USER_METADATA_CACHE_ENABLED`, `AlluxioURI`, and command base context.

Risks and test signals: failures are runtime exceptions and not typed `URIStatus` responses. The error message for bad underlying local-cache filesystem reports the outer class name, which may reduce diagnostics. It centralizes important guard behavior for all subcommands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/AbstractMetadataCacheSubCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropAllCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropAllCommand.java

Purpose: FUSE metadata-cache subcommand that clears all cached metadata entries.

Important APIs and helpers: `getCommandName()` returns `dropAll`; `getUsage()` builds the synthetic FUSE CLI path; `runSubCommand` calls `MetadataCachingFileSystem.dropMetadataCacheAll()` and returns a completed `URIStatus`; `getDescription()` describes the clear-all behavior.

Control flow and state: actual cache mutation is delegated to the metadata-caching filesystem. The command returns a mock `FileInfo` with `completed=true` so FUSE shell calls can surface success through file metadata.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `AlluxioURI`, `URIStatus`, `FileInfo`, and `Constants`.

Risks and test signals: no argument validation is implemented because no arguments are expected. It relies on the abstract base to enforce cache-enabled state and filesystem type.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropAllCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropCommand.java

Purpose: FUSE metadata-cache subcommand that clears cached metadata for the target path and related entries.

Important APIs and helpers: `getCommandName()` returns `drop`; `getUsage()` includes a path placeholder before `.alluxiocli.metadatacache.drop`; `runSubCommand` calls `MetadataCachingFileSystem.dropMetadataCache(path)` and returns a completed `URIStatus`; `getDescription()` explains path/children invalidation.

Control flow and state: the path supplied by `FuseShell` is the parent path of the special command suffix. Cache mutation is delegated to the metadata-caching filesystem.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `AlluxioURI`, `URIStatus`, `FileInfo`, and `Constants`.

Risks and test signals: no extra args are validated, so all path targeting depends on `FuseShell` parent-path parsing. Description contains a grammatical typo but documents recursive directory behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/DropCommand.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/SizeCommand.java -->
# sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/SizeCommand.java

Purpose: FUSE metadata-cache subcommand that exposes current metadata-cache size through returned file metadata.

Important APIs and helpers: `getCommandName()` returns `size`; `getUsage()` builds the synthetic `.alluxiocli.metadatacache.size` path; `runSubCommand` calls `MetadataCachingFileSystem.getMetadataCacheSize()` and returns a completed `URIStatus` with `FileInfo.length` set to that value.

Control flow and state: no cache mutation occurs. The command uses the `ls -l` file-size field as the user-visible transport for cache size.

Dependencies and integration: depends on `AbstractMetadataCacheSubCommand`, `MetadataCachingFileSystem`, `URIStatus`, `FileInfo`, `AlluxioURI`, and `Constants`.

Risks and test signals: size semantics depend on the underlying metadata-cache implementation. Like other subcommands, validation and filesystem-type checks are centralized in the abstract base.
<!-- END_FILE_RESEARCH: sources/distributed-fs/alluxio/integration/fuse/src/main/java/alluxio/cli/command/metadatacache/SizeCommand.java -->
