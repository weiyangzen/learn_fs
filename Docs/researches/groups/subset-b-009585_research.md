# subset-b-009585 gcsx read, prefix, and sync research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket.go

## Scope

This file implements `prefixBucket`, a `gcs.Bucket` decorator that presents a virtual bucket rooted at a configured object-name prefix. Calls entering the wrapper use local names without the prefix; calls leaving for the wrapped bucket prepend the prefix; returned object and folder names have the prefix stripped before they reach callers.

## Purpose

`NewPrefixBucket` lets higher layers mount or operate on a subtree-like view of a bucket without changing the underlying storage implementation. It preserves object-name UTF-8 invariants by rejecting invalid UTF-8 prefixes, and it delegates all persistence to the wrapped `gcs.Bucket`.

## Important APIs, Types, And Functions

- `NewPrefixBucket(prefix, wrapped)` validates `prefix` and returns a `gcs.Bucket`.
- `prefixBucket.wrappedName` and `localName` are the central name translators.
- Read paths: `NewReaderWithReadHandle` and `NewMultiRangeDownloader`.
- Write paths: `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, `FinalizeUpload`, and `FlushPendingWrites`.
- Mutation paths: `CopyObject`, `ComposeObjects`, `UpdateObject`, `DeleteObject`, `MoveObject`.
- Namespace paths: `ListObjects`, `GetFolder`, `CreateFolder`, `DeleteFolder`, `RenameFolder`.
- Metadata forwarding: `Name`, `BucketType`, and `GCSName`.

## Control Flow

Most methods clone the incoming request struct, rewrite only the name fields, call the wrapped bucket, and then strip the prefix from returned `Object`, `MinObject`, `Folder`, or listing names. `ListObjects` prepends the wrapper prefix to the request prefix and then trims it from both object names and collapsed runs. Compose rewrites every source name plus the destination name.

## State And Persistence Behavior

The wrapper stores only `prefix` and `wrapped`; all durable object, folder, upload, read-handle, and generation state lives in the wrapped bucket. Chunk and append writers are returned directly from the wrapped bucket, so finalization and flush are where returned min-object names are localized.

## Dependencies And Integration Points

The implementation depends on `internal/storage/gcs` bucket interfaces, `strings.TrimPrefix`, `unicode/utf8`, and `context`. It integrates with fake buckets and storage utilities in tests, with hierarchical namespace folder APIs, with multi-range downloading, and with GCS read handles.

## Risks And Maintenance Notes

Name translation must be kept complete as `gcs.Bucket` grows. Any new method that accepts or returns object/folder names needs explicit prefix mapping. `localName` uses `strings.TrimPrefix`, so it silently returns unchanged names if a wrapped implementation returns an object outside the prefix; this is useful for defensive behavior but may hide wrapped-bucket bugs. `RenameFolder` prefixes `destinationFolderId` as though it is a folder name; this is correct only if that field semantically expects a prefixed name/id in the wrapped API. `GCSName` composes with `wrapped.GCSName(object)`, so wrappers beneath this one can affect final naming.

## Test Signals

Coverage comes from `prefix_bucket_test.go`: normal reads, read handles, MRD reads and errors, object create/copy/compose/stat/list/update/delete, chunk writer finalize/flush, appendable writer flows, folders, and hierarchical object move. The tests assert both local returned names and back-door wrapped-bucket storage names.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket_test.go

## Scope

This test suite validates the `prefixBucket` decorator against a `fake.Bucket` using both suite-style and plain `testing` cases. It is a broad behavior test for prefix rewriting across the bucket API surface.

## Purpose

The tests ensure callers see unprefixed names while the wrapped bucket receives and stores prefixed names. They also protect pass-through behavior for non-name metadata, read handles, MRD, folders, and hierarchical namespace operations.

## Important APIs, Types, And Functions

- `PrefixBucketTest` sets up `context.Background`, prefix `foo_`, a fake wrapped bucket, and `gcsx.NewPrefixBucket`.
- Tests cover `Name`, `NewReaderWithReadHandle`, `NewMultiRangeDownloader`, `CreateObject`, chunk and append writers, `CopyObject`, `ComposeObjects`, `StatObject`, `ListObjects`, `UpdateObject`, and `DeleteObject`.
- Standalone tests cover `GetFolder`, `DeleteFolder`, `RenameFolder`, `CreateFolder`, and `MoveObject`.

## Control Flow

Most cases create state directly in the wrapped bucket, operate through the prefix bucket using suffix names, and then inspect returned names or read from the wrapped bucket using prefixed names. Listing tests create mixed prefixed and unprefixed objects to verify filtering and trimming. MRD tests add one or more ranges and either wait explicitly or verify close behavior.

## State And Persistence Behavior

The fake bucket is the authoritative backing store. The tests deliberately bypass the wrapper for setup and verification, which catches missing prefix prepending. Chunk writer and appendable writer tests verify that upload state can be created through the wrapper and finalized or flushed with localized returned names.

## Dependencies And Integration Points

The suite uses `storageutil` for direct object setup/readback, `fake.NewFakeBucket`, `gcs` request types, `stretchr/testify`, `suite`, and `timeutil.RealClock`. Hierarchical namespace tests use fake bucket capabilities for folder and move operations.

## Risks And Maintenance Notes

The test suite is strong on happy paths and several MRD errors but does not exhaustively test every request field copied through the wrapper. It also has a few assertion oddities, such as `assert.Nil(nil, err)`, that still express intent but are easy to misread. If `gcs.Bucket` semantics change around folder IDs, read handles, or collapsed listing runs, these tests should be revisited.

## Test Signals

Signals include preservation of bucket name, successful read-handle propagation and returned opaque handle, full and partial MRD output, non-existent and out-of-bounds MRD failures, localization of returned object/folder names, correct delimiter behavior when the delimiter appears in the mount prefix, and deletion/move visibility through `NotFoundError`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/prefix_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/random_reader.go

## Scope

This file implements the legacy `RandomReader` for reading byte ranges from one generation of one GCS object. It combines file-cache reads, sequential range-reader reuse, adaptive random/sequential classification, optional MRD use for zonal random reads, read-handle reuse, metrics, tracing, and cleanup.

## Purpose

`RandomReader` is optimized for FUSE read workloads where the kernel may issue sequential, readahead, random, or parallel reads. It tries the local file cache first, reuses a GCS range reader when profitable, expands small sequential requests into larger GCS ranges, and switches to MRD for random reads on zonal buckets.

## Important APIs, Types, And Functions

- Constants: `minReadSize`, `maxReadSize`, `minSeeksForRandom`, `TimeoutForMultiRangeRead`, `FallbackToNewRangeReader`.
- `RandomReader` interface: `CheckInvariants`, `ReadAt`, `Object`, `Destroy`.
- `ObjectData` returns a buffer, size, and cache-hit flag.
- `ReaderType` chooses `RangeReader` or `MultiRangeReader`.
- `NewRandomReader` constructs a `randomReader`.
- Cache path: `tryReadingFromFileCache`.
- Read classification: `isSeekNeeded`, `getReadInfo`, `getEndOffset`, `readerType`.
- Range path: `startRead`, `readFull`, `skipBytes`, `invalidateReaderIfMisalignedOrTooSmall`, `readFromExistingRangeReader`, `readFromRangeReader`, `closeReader`.
- MRD path: `readFromMultiRangeReader`.

## Control Flow

`ReadAt` rejects offsets at or beyond object size with `io.EOF` and rejects negative offsets. It tries file cache first; a cache hit, full-buffer read, or EOF-completing partial read returns immediately. Otherwise it classifies the access pattern. Range reads take `rr.mu`, optionally recompute classification for zonal buckets if another read advanced state, reuse or replace an existing reader, start a new GCS range if necessary, and read via `io.ReadFull`. MRD reads go through `MultiRangeDownloaderWrapper` and increment a wrapper refcount once per reader lifetime.

## State And Persistence Behavior

Reader state includes the current `gcs.StorageReader`, cancel function, `[start, limit)` range, read handle from the last closed reader, expected next offset, seek count, total bytes read, and current read type. File-cache state is guarded separately by `fileCacheMu` and stores a reusable `CacheHandle`. Durable data is not stored here; cache contents are delegated to file cache infrastructure and remote reads/writes to `gcs.Bucket`. `Destroy` closes the active GCS reader, closes any cache handle, and decrements MRD wrapper refcount if MRD was used.

## Dependencies And Integration Points

This code depends on `cfg`, file cache and LRU utilities, GCS storage interfaces, GCSFuse clobber errors, logging, metrics, tracing, FUSE handle IDs, and `MultiRangeDownloaderWrapper`. It integrates with `InactiveTimeoutReader` when configured, `gcs.ReadObjectRequest.ReadHandle`, `gcs.MinObject` generation and gzip metadata, and cache exclusion/fallback errors.

## Risks And Maintenance Notes

The implementation has several coupled concurrency domains: `mu` for range reader state, atomics for read classification, and `fileCacheMu` for cache handle access. It is documented as not safe for concurrent access, yet MRD and atomics support some concurrent behavior; future changes should be explicit about supported access patterns. Cache failures are intentionally split between fallback and fatal errors, so new cache errors must be classified carefully. EOF handling depends on range limits being accurate. Read-handle reuse depends on closing readers before creating replacement readers. Zonal bucket logic recomputes classification to avoid using range readers after another read has made MRD more appropriate.

## Test Signals

The deprecated ogletest suite and newer testify suite cover empty and EOF reads, existing-reader reuse, skipping, reader exhaustion, timeout and cancellation behavior, expanded sequential ranges, random read sizing, cache hits/misses/invalidation/deletion, file clobber conversion, read-handle propagation, extra/short reader data, MRD for zonal random reads, MRD refcounts, invalid offsets, inactive stream timeout wrapping, and read-type transitions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_stretchr_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_stretchr_test.go

## Scope

This is the newer testify-based test suite for `randomReader`. It focuses on read classification, range-reader state transitions, MRD behavior, concurrency, read-handle propagation, and inactive timeout reader configuration.

## Purpose

The suite supplements the deprecated ogletest file with targeted tests for newer behavior, especially zonal-bucket MRD selection and bug fixes around seek accounting.

## Important APIs, Types, And Functions

- `RandomReaderStretchrTest` creates a `storage.TestifyMockBucket`, object metadata, cache manager, and `checkingRandomReader`.
- `Test_GetReadInfo`, `Test_IsSeekNeeded`, `Test_GetEndOffset`, and `Test_ReaderType` validate classification helpers.
- `Test_ReadFromRangeReader_*` exercises direct range-reader internals.
- `Test_ReadAt_ValidateReadType`, `Test_ReadAt_ValidateZonalRandomReads`, and MRD tests exercise public `ReadAt` strategy selection.
- `Test_ReadAt_WithAndWithoutReadConfig` validates `InactiveTimeoutReader` creation.

## Control Flow

Tests set internal `randomReader` fields directly to model existing readers, seek counts, read types, read handles, and object sizes. Mock expectations verify exact `gcs.ReadObjectRequest` ranges and read handles. MRD tests create `MultiRangeDownloaderWrapper` and fake MRD instances, then assert range-reader calls are avoided for zonal random reads.

## State And Persistence Behavior

The suite inspects transient reader state after each call: `reader`, `cancel`, `start`, `limit`, `readHandle`, `expectedOffset`, `seeks`, `totalReadBytes`, `isMRDInUse`, and MRD wrapper refcount. It uses generated in-memory byte slices and fake readers rather than durable storage.

## Dependencies And Integration Points

It depends on testify `suite`, `mock`, `assert`, and `require`; fake GCS readers and multi-range downloaders; file cache setup helpers; metrics constants; `cfg.ReadConfig`; and the `MultiRangeDownloaderWrapper`.

## Risks And Maintenance Notes

Many tests intentionally reach into unexported state, so they are sensitive to internal refactors. This is useful for protecting tricky invariants but increases maintenance cost. Several tests manually call `SetupTest`/`TearDownTest` inside subtests, so cleanup ordering matters. MRD expectations assume specific bucket type call counts and can become brittle if strategy selection is rearranged.

## Test Signals

Signals include random/sequential transition thresholds, average-read-size prefetch sizing, range-reader close and read-handle capture, detection of short and overlong readers, invalid offset errors, MRD-only reads on zonal random access, parallel MRD read accounting, nil MRD wrapper failure, and correct inactive-timeout wrapping only when configured.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_stretchr_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_test.go

## Scope

This deprecated ogletest suite still provides broad regression coverage for `randomReader`, especially historical range-reader reuse and file-cache interactions. A file comment directs new tests to the testify suite.

## Purpose

The tests protect long-standing behavior: object bounds, reader invariants, cancellation, range expansion, cache population and fallback, cache invalidation, deleted cache files, destroy cleanup, and file clobber handling.

## Important APIs, Types, And Functions

- `checkingRandomReader` wraps `randomReader` with invariant checks around reads and destroy.
- Helper matchers verify GCS request range starts and limits.
- `countingCloser` and `blockingReader` model close counts and context cancellation.
- `RandomReaderTest` runs for both regular and zonal/hierarchical bucket types.

## Control Flow

Tests create mock buckets and fake readers, set up object metadata, perform reads through `checkingRandomReader.ReadAt`, and assert returned `ObjectData`, buffer contents, mock calls, and internal state. File-cache tests use a real cache handler/job manager rooted under `$HOME/cache/dir` and fake GCS content to verify first-read miss and later-hit behavior.

## State And Persistence Behavior

The suite verifies that reader state advances across reads, active readers remain open when not exhausted, exhausted readers close, cache handles are created, invalidated, closed, or retained as expected, and `Destroy` releases cache handles. Cache tests also inspect downloader job status and cache files on disk.

## Dependencies And Integration Points

It uses ogletest/oglemock, `storage.MockBucket`, fake readers, file cache and downloader infrastructure, LRU cache, disk block-size detection, metrics/tracing noops, FUSE read op context, and GCSFuse clobber errors.

## Risks And Maintenance Notes

The file is deprecated but still important because it covers realistic file-cache workflows not fully duplicated elsewhere. It writes under `$HOME/cache/dir`, so test isolation depends on environment behavior. Mock call counts vary by bucket type and cache path, and several tests depend on Linux semantics for deleting an open file.

## Test Signals

Signals include no-op empty reads, EOF at object size, offset errors, new reader error wrapping, timeout wrapping, cancellation only while blocked, sequential read expansion to object or configured size, average-size random expansion, cache hit after full-object read, cache behavior for random reads with `cacheFileForRangeRead`, fallback after invalid jobs/handles, deleted cache file behavior with and without open handles, failed job restart, `tryReadingFromFileCache` hit/miss paths, and `FileClobberedError` wrapping on GCS not found.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/random_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/mock_read_manager.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/mock_read_manager.go

## Scope

This file defines a testify mock implementation of `gcsx.ReadManager` for read-manager wrapper tests.

## Purpose

`MockReadManager` lets tests assert delegation from wrappers such as `VisualReadManager` without constructing real GCS/cache readers.

## Important APIs, Types, And Functions

- `MockReadManager` embeds `gcsx.ReadManager` and `mock.Mock`.
- `ReaderName` returns `mock_read_manager`.
- `ReadAt`, `Object`, `Destroy`, and `CheckInvariants` dispatch to testify `Called`.

## Control Flow

Each mocked method records and returns configured expectations. `ReadAt` type-asserts the first return value to `gcsx.ReadResponse`; `Object` type-asserts to `*gcs.MinObject`.

## State And Persistence Behavior

No production state is stored beyond testify mock call history and configured return values.

## Dependencies And Integration Points

It depends on `context`, `gcsx` reader contracts, `gcs.MinObject`, and `stretchr/testify/mock`. It is used by `visual_read_manager_test.go`.

## Risks And Maintenance Notes

Tests must configure all methods that will be called; otherwise testify will fail or type assertions can panic if return slots are missing or nil. If `ReadManager` grows new required methods, this mock must be updated.

## Test Signals

The file itself has no direct tests, but `visual_read_manager_test.go` exercises its method expectations for `Object`, `ReadAt`, and `Destroy`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/mock_read_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager.go

## Scope

This file implements the newer compositional `ReadManager`, which orders multiple `gcsx.Reader` implementations for one object and falls back between them.

## Purpose

`ReadManager` centralizes read orchestration for a file handle. It can prioritize shared chunk cache or traditional file cache, optionally use buffered prefetch reads, and always keep a GCS reader as the final fallback. A shared `ReadTypeClassifier` coordinates read-pattern decisions across those readers.

## Important APIs, Types, And Functions

- `ReadManager` stores object metadata, ordered readers, classifier, and trace handle.
- `ReadManagerConfig` carries cache handlers, MRD wrapper, metrics/tracing, buffered-read knobs, worker pool, semaphore, handle ID, and initial offset.
- `NewReadManager` constructs the reader chain.
- `ReadAt` performs EOF/empty-read handling, sets `req.ReadInfo`, tries readers in order, and records successful reads.
- `CheckInvariants`, `Object`, `ReaderName`, and `Destroy` implement `gcsx.ReadManager`.

## Control Flow

Construction adds one cache reader if configured: shared chunk cache takes precedence over traditional file cache. It then optionally adds a `bufferedread.BufferedReader` if enabled and constructible. Finally it appends `client_readers.GCSReader`. On read, the manager gets current read info, starts a trace span per reader, and advances through the chain only when the reader returns `gcsx.FallbackToAnotherReader`.

## State And Persistence Behavior

The manager itself stores no durable content. It records read pattern state in `ReadTypeClassifier`; cache persistence is handled by cache readers; GCS state is handled by the bucket/client readers. `Destroy` delegates cleanup to every reader in chain order.

## Dependencies And Integration Points

It integrates with `gcsx.FileCacheReader`, `gcsx.SharedChunkCacheReader`, `bufferedread.BufferedReader`, `client_readers.GCSReader`, file cache config, worker pools, semaphores, metrics, tracing, and FUSE handle IDs.

## Risks And Maintenance Notes

Reader order is behaviorally significant. Shared chunk cache and traditional file cache are mutually exclusive in construction; passing both uses shared chunk cache. `config.Config` is dereferenced for buffered-read settings, so callers must provide a non-nil config. Any reader returning a non-fallback error stops the chain, so reader implementations must reserve hard errors for cases that should not fall back. `ReadAt` mutates the request by setting `ReadInfo`; fallback readers depend on `Offset` and `Buffer` remaining unchanged.

## Test Signals

`read_manager_test.go` covers reader-chain construction with file cache, shared absence, buffered read, and buffered creation failure; invalid offsets; GCS errors; clobbered files; full-object cache hit; fallback from first to second reader; and buffered fallback to GCS.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager_test.go

## Scope

This testify suite validates the new compositional `ReadManager` for both non-zonal and zonal bucket types.

## Purpose

The tests protect reader-chain construction, simple read behavior, fallback semantics, file-cache integration, and error propagation.

## Important APIs, Types, And Functions

- `readManagerConfig(fileCacheEnable, bufferedReadEnable)` builds test configs with optional cache handler and worker pool.
- `mockNewReaderWithHandleCallForTestBucket` matches GCS range requests.
- `readAt` wraps `ReadManager.ReadAt` with invariant checks.
- Test cases cover construction combinations, EOF, GCS errors, clobbering, cache hit, and fallback.

## Control Flow

`SetupTest` creates object metadata, a testify mock bucket, context, and default read manager with file cache enabled. Individual tests override config or construct synthetic managers with mock readers to isolate fallback logic. Buffered-read tests start and stop a worker pool when needed.

## State And Persistence Behavior

The suite checks `readers` slice composition and uses cache directories under `$HOME/test_cache_dir` for file cache behavior. It verifies that a first read can populate cache and a second read succeeds without additional GCS reads. `TearDownTest` destroys the manager and stops worker pools.

## Dependencies And Integration Points

It integrates with `bufferedread`, file cache/downloader/LRU, `client_readers.GCSReader`, `gcsx.MockReader`, fake readers, storage testify mocks, semaphores, worker pools, metrics/tracing noops, and clobber error types.

## Risks And Maintenance Notes

The construction assertions rely on concrete reader types and exact ordering. File-cache tests touch filesystem paths outside `t.TempDir` unless explicitly removed. Buffered creation failure is simulated by a zero-weight semaphore; if buffered reader initialization changes, that test may need updating.

## Test Signals

Signals include expected reader counts and concrete types for each config, empty-read success, EOF for reads at/past object size, network error propagation, timeout propagation, `FileClobberedError` wrapping on not found, cache reuse on repeated full-object reads, fallback on `FallbackToAnotherReader`, and no fallback on hard errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/read_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager.go

## Scope

This file implements `VisualReadManager`, a `gcsx.ReadManager` wrapper that records requested read ranges and renders a workload insight visualization when destroyed.

## Purpose

The wrapper provides optional observability for file read patterns without changing the underlying read implementation. It can print the visualization to stdout or append it to a configured output file.

## Important APIs, Types, And Functions

- `VisualReadManager` stores the wrapped manager, renderer, recorded ranges, mutex, workload insight config, and forward merge threshold.
- `NewVisualReadManager` constructs the wrapper.
- `ReadAt` records a range for non-empty buffers and delegates to the wrapped manager.
- `Destroy` renders and outputs the visualization, then destroys the wrapped manager.
- `acceptRange`, `mergeRanges`, and `appendToFile` implement range collection and output.

## Control Flow

`ReadAt` records `[Offset, Offset+len(Buffer))` before the wrapped read runs. `acceptRange` clamps the end to object size, then tries to merge only with the last recorded range. `mergeRanges` merges adjacent or forward-near ranges within the configured threshold, but does not merge overlapping ranges. `Destroy` renders using object name, object size, and accumulated ranges.

## State And Persistence Behavior

Recorded ranges live in memory until `Destroy`. Output persistence is append-only to `cfg.OutputFile` with mode `0600`; if no file is configured, output goes to stdout. The wrapper does not persist read results or cache content.

## Dependencies And Integration Points

It depends on `cfg.WorkloadInsightConfig`, `workloadinsight.Renderer`, `workloadinsight.Range`, `logger`, and the `gcsx.ReadManager` interface. It is intended to wrap any concrete read manager.

## Risks And Maintenance Notes

The wrapper records attempted reads before knowing whether they succeed, so visual output may include failed reads. It only merges with the most recent range and refuses overlapping merges, which preserves request chronology but may fragment repeated/overlapping workloads. `Destroy` calls `Object()` during rendering; wrapped managers must still be valid. Output failures print to stdout and warn, so callers do not receive an error.

## Test Signals

`visual_read_manager_test.go` validates construction, range acceptance, adjacent and threshold-based merging, non-merging overlaps, read delegation, destroy delegation, output file creation, append behavior, and empty output-path errors.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager_test.go

## Scope

This file tests the visual read-manager wrapper and its file append helper using `MockReadManager` and the workload insight renderer.

## Purpose

The tests ensure the wrapper records ranges, merges only the intended range patterns, delegates reads and destroy calls, and writes visualization output when configured.

## Important APIs, Types, And Functions

- `TestNewVisualReadManager` validates constructor wiring.
- `TestVisualReadManager_AcceptRange` covers range recording and last-range merging.
- `TestVisualReadManager_MergeRanges` covers overlap, adjacency, gap, and forward-threshold cases.
- `TestVisualReadManager_ReadAt` verifies recording plus delegated read.
- `TestVisualReadManager_Destroy` and output-file variants verify rendering/destroy behavior.
- `TestAppendToFile_*` validates append helper behavior.

## Control Flow

Tests create mock read managers with optional `Object`, `ReadAt`, and `Destroy` expectations, instantiate a real workload insight renderer, invoke wrapper internals or public methods, and inspect in-memory ranges or output files.

## State And Persistence Behavior

Most state is in `vrm.readIOs`. File-output tests write `test_output.txt` or `test_append_output.txt` in the current package directory and remove them after assertions.

## Dependencies And Integration Points

It depends on `cfg.WorkloadInsightConfig`, `gcsx.ReadRequest`, `gcs.MinObject`, workload insight rendering, testify `assert/mock/require`, and local `MockReadManager`.

## Risks And Maintenance Notes

Tests for internal helpers are intentionally white-box. Output-file tests use fixed relative filenames, so interrupted tests can leave artifacts. The accept-range expectations document the current non-overlap merge rule; changing that rule will require coordinated test updates.

## Test Signals

Signals include empty initial state, exact range list after non-overlapping/overlapping/adjacent/mixed inputs, threshold merge boundaries in MB, one recorded range for a delegated read, non-empty rendered output files, append preserving previous content, and error on empty output path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_manager/visual_read_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier.go

## Scope

This file implements `ReadTypeClassifier`, the newer shared read-pattern classifier used by the compositional read manager and reader stack.

## Purpose

The classifier tracks expected offsets, seeks, total read bytes, initial offset, and current read type so cache, buffered, and GCS readers can make consistent sequential-vs-random decisions.

## Important APIs, Types, And Functions

- `ReadInfo` carries `ReadType`, `ExpectedOffset`, and `SeekRecorded` for one request.
- `ReadTypeClassifier` stores atomic read type, expected offset, seek count, total bytes, configured sequential read size, and initial offset.
- `NewReadTypeClassifier`, `RecordSeek`, `RecordRead`, `GetReadInfo`, `ComputeSeqPrefetchWindowAndAdjustType`, `IsReadSequential`, `NextExpectedOffset`, `avgReadBytes`, and `GetSeeks`.

## Control Flow

`GetReadInfo` snapshots state, optionally records a seek, computes average read size, and classifies as sequential when average read size is at least `maxReadSize` or no seeks have occurred and the initial offset is zero. Otherwise it classifies as random. `RecordRead` adds bytes and advances expected offset. `ComputeSeqPrefetchWindowAndAdjustType` returns configured sequential size for sequential patterns or a rounded/clamped random read window for random patterns.

## State And Persistence Behavior

All mutable state is in atomics, making the classifier safe for concurrent use. It persists only in memory for a file handle or reader lifetime; it does not write cache or remote state.

## Dependencies And Integration Points

It depends on metrics read-type constants and shares size constants with the older random-reader heuristics. `read_manager.go` creates one classifier per read manager and passes `ReadInfo` down through `ReadRequest`.

## Risks And Maintenance Notes

Classification behavior differs from the old `randomReader.getReadInfo`: a first read at non-zero initial offset can immediately classify random even before a seek. Concurrent callers get atomic consistency but not transaction-like ordering between `GetReadInfo` and `RecordRead`; tests allow final read type to vary under concurrency. Division by seeks is guarded, but average-read semantics depend on whether seeks are counted before or after reads.

## Test Signals

`read_type_classifier_test.go` validates initial state, seek detection, `GetReadInfo` and `RecordSeek`, `RecordRead`, prefetch window sizing and clamping, sequential predicate, average byte calculation, sequential and random read simulations, random-to-sequential transition after large reads, and concurrent updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier_test.go

## Scope

This test file validates `ReadTypeClassifier` in isolation, including helper methods and concurrent state updates.

## Purpose

The tests lock down the newer classifier heuristics that are shared across the read-manager reader chain.

## Important APIs, Types, And Functions

- Tests cover `NewReadTypeClassifier`, `isSeekNeeded`, `GetReadInfo`, `RecordSeek`, `RecordRead`, `ComputeSeqPrefetchWindowAndAdjustType`, `IsReadSequential`, `avgReadBytes`, and `GetSeeks` indirectly.
- Scenario tests model sequential reads, random reads, random-to-sequential transitions, and concurrent updates.

## Control Flow

Most tests seed atomic fields directly, call one classifier method, and assert read type, seek count, expected offset, total bytes, or returned window. Scenario tests call `RecordSeek` before reads and `RecordRead` after reads to mirror production ordering.

## State And Persistence Behavior

The tests inspect in-memory atomic state only. The concurrent test launches ten goroutines performing repeated seek/read updates and then asserts total byte accumulation and a valid final read type.

## Dependencies And Integration Points

It depends on `metrics` read-type constants, Go `sync.WaitGroup`, and testify assertions. It also uses `maxReadSize`, `minReadSize`, and `sequentialReadSizeInMb` from the gcsx test package context.

## Risks And Maintenance Notes

The tests document subtle policy choices: first non-zero offset is random, any sequential seek can switch to random, large average reads switch back to sequential, and random prefetch windows are rounded up to MB boundaries. Concurrency assertions intentionally avoid deterministic read-type expectations because update interleaving is nondeterministic.

## Test Signals

Signals include no seek when expected offset is zero, seek on backward or too-large forward sequential jumps, seek on non-contiguous random reads, no double-count when `seekRecorded` is true, expected offset update after reads, prefetch windows from 1 MiB through configured sequential size, integer-division average behavior, and exact byte totals under concurrent updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/read_type_classifier_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/reader.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/reader.go

## Scope

This file defines the shared reader contracts used by the newer gcsx read stack.

## Purpose

It provides common request/response structures and interfaces so cache readers, buffered readers, GCS readers, visual wrappers, and read managers can interoperate and fall back cleanly.

## Important APIs, Types, And Functions

- `FallbackToAnotherReader` signals that the caller should try the next reader.
- `ReadRequest` carries caller buffer, offset, optional size-check bypass, and embedded `ReadInfo`.
- `GCSReaderRequest` carries lower-level GCS buffer, offset, computed end offset, force-create-reader flag, skip-size-check flag, and read info pointer.
- `ReadResponse` carries returned data chunks, size, and optional completion callback.
- `Reader`, `ReadManager`, and `GCSReader` interfaces define the common behavior.

## Control Flow

There is no executable flow beyond interface contracts. The key protocol is that `Reader.ReadAt` either fills `ReadRequest.Buffer`, returns data slices in `ReadResponse.Data`, or returns `FallbackToAnotherReader` to allow read-manager fallback. The read manager preserves `Offset` and `Buffer` across fallback attempts.

## State And Persistence Behavior

This file has no mutable state except the package-level sentinel error. Persistence and resource ownership are delegated to concrete implementations.

## Dependencies And Integration Points

It depends on `context`, `errors`, and `gcs.MinObject`. It is consumed by read-manager, file-cache reader, shared chunk cache reader, buffered reader integration, client GCS readers, mocks, and visual wrappers.

## Risks And Maintenance Notes

The fallback sentinel is part of the cross-reader control contract; wrapping must preserve `errors.Is`. `ReadResponse.Data` plus direct buffer filling creates two data-return modes, so callers must understand both. `Callback` adds post-read lifecycle behavior that can be missed if callers only inspect size.

## Test Signals

There are no direct tests for this definitions file, but almost every read-manager and reader test exercises these contracts through successful reads, fallback errors, EOF handling, and mock expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader.go

## Scope

This file implements `SharedChunkCacheReader`, a `gcsx.Reader` that serves reads from a shared on-disk chunk cache and downloads missing chunks on demand.

## Purpose

The reader supports shared-cache deployments, especially NFS-like environments, by avoiding whole-file prefetch and instead caching only chunks needed by reads. It falls back to the next reader when cache operations or chunk downloads fail.

## Important APIs, Types, And Functions

- `SharedChunkCacheReader` stores a shared chunk cache manager, bucket, object metadata, metrics/tracing handles, and FUSE handle ID.
- `NewSharedChunkCacheReader` constructs the reader.
- `ReadAt` checks exclusion/bounds, reads across chunk boundaries, opens cached chunks directly, downloads missing chunks, fills the caller buffer, and returns `ReadResponse`.
- `downloadChunk` creates temporary chunk files, downloads from GCS range reads, closes/syncs, and atomically renames to final chunk path.
- `ReaderName`, `CheckInvariants`, and `Destroy` implement `Reader`.

## Control Flow

`ReadAt` returns fallback immediately for excluded objects. It validates offset, logs and starts metrics timing, then loops while the buffer has remaining bytes and the object has data. For each chunk it computes chunk index and byte limits, tries `os.Open`, downloads on `ENOENT`, reopens the chunk, reads the requested slice with `ReadAt`, and advances counters. Non-ENOENT open errors, download errors, incomplete reads, and corrupted chunks return `FallbackToAnotherReader`.

## State And Persistence Behavior

The reader itself is stateless between reads. Persistent state lives in chunk files under manager-derived object/generation directories. Downloads use unique temporary paths, write the full chunk, close the file, and `os.Rename` atomically to the final chunk path. Directory recreation handles one LRU eviction race. `Destroy` is a no-op.

## Dependencies And Integration Points

It depends on `file.SharedChunkCacheManager`, GCS bucket range reads, metrics file-cache counters, logging, UUID request IDs, OS file APIs, syscall errno checks, and FUSE handle IDs. `read_manager.go` installs it before other readers when a shared chunk cache manager is configured.

## Risks And Maintenance Notes

Concurrent downloads of the same chunk can race at rename time; one may fail and fall back, depending on temp-path and final rename behavior. `defer chunkFile.Close()` inside the loop defers all closes until the full read returns, which is simple but can hold multiple descriptors for large reads. Metrics classify offset zero as sequential and all others as random, not using `ReadInfo`. Partial data copied into the caller buffer before fallback is returned with response size zero, so fallback callers must overwrite or ignore partial buffer contents.

## Test Signals

`shared_chunk_cache_reader_test.go` covers construction, single-chunk read, cache hit without file modification, cross-boundary reads, EOF, negative offset, partial tail reads, regex exclusion fallback, full multi-chunk reads, zero-length reads, concurrent reads, same-chunk race behavior, deleted directory recovery, download failure fallback, corrupted cache fallback, and GCS read failure fallback.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader_test.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader_test.go

## Scope

This suite validates `SharedChunkCacheReader` using temporary cache directories and fake GCS buckets.

## Purpose

The tests protect on-demand chunk caching behavior, chunk-boundary reads, cache hits, concurrency, fallback conditions, and resilience to cache directory races.

## Important APIs, Types, And Functions

- `sharedChunkCacheReaderTest` sets up a temp cache dir, `SharedChunkCacheManager`, fake bucket, object data, and reader.
- Suite tests cover constructor, single and multi-chunk reads, cache hits, EOF/negative/partial/zero reads, and exclusion regex.
- Standalone tests cover concurrent reads, same-chunk race, deleted directory recovery, download permission failure, corrupted cached chunk, and GCS download failure.

## Control Flow

Tests create deterministic byte-pattern objects in a fake bucket, call `ReadAt` with offsets and buffers, and verify response sizes, buffer contents, chunk file existence, and error types. Failure tests manipulate filesystem permissions, truncate chunk files, or use missing fake-bucket objects.

## State And Persistence Behavior

The cache directory is `t.TempDir()` in all major tests, so chunk files are isolated. Tests inspect chunk paths derived from bucket name, object name, generation, and chunk index. Cache-hit behavior is verified by comparing chunk file modification time before and after the second read.

## Dependencies And Integration Points

It depends on `file.NewSharedChunkCacheManager`, `fake.NewFakeBucket`, `gcs.CreateObjectRequest`, metrics/tracing noops, `timeutil.RealClock`, testify suite/assert/require, and OS file operations.

## Risks And Maintenance Notes

Permission-denied behavior can vary when tests run with elevated privileges or unusual filesystems. The same-chunk race test asserts success for all goroutines and a final chunk file but does not prove only one remote download occurred. The tests validate fallback error types, not integration with read-manager fallback overwrite behavior.

## Test Signals

Signals include exact data equality for chunk reads, chunk files created for every needed chunk, modification time unchanged on cache hit, EOF at object size, negative offset error text, partial tail size of remaining bytes, `FallbackToAnotherReader` for exclusions and failures, successful concurrent reads, directory recreation after deletion, and corrupted chunk detection via short read.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/shared_chunk_cache_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/syncer.go

## Scope

This file defines and implements `Syncer`, the write-back component that syncs a mutable local `TempFile` to a GCS object generation.

## Purpose

`Syncer` avoids unnecessary uploads when local content is unchanged, writes new local files fully, and can optimize append-only changes by composing a temporary appended blob with the original object when safe and supported.

## Important APIs, Types, And Functions

- `Syncer` interface exposes `SyncObject`.
- `NewSyncer` chooses a full-object creator and, unless rapid writes are enabled, a compose creator.
- `fullObjectCreator.Create` builds a `gcs.CreateObjectRequest` from source metadata and uploads full contents.
- `objectCreator` abstracts full and compose upload paths.
- `newSyncer` wires thresholds, retry/timeout settings, and creators.
- `syncer.SyncObject` implements dirty-state decisions and upload/compose selection.

## Control Flow

`SyncObject` stats the temp file. If there is no source object, it seeks to the beginning and uploads the full local file. For existing objects, it validates dirty threshold against finalized source size, returns early if `Mtime` is nil, and for finalized objects returns early if size and dirty threshold match source size. Otherwise, it composes only when compose is available, source size meets threshold, dirty threshold equals source size, and component count is below the GCS max; otherwise it seeks to the beginning and uploads the full object.

## State And Persistence Behavior

The syncer stores configuration thresholds and creator dependencies only. Durable effects are new GCS object generations, and possibly temporary compose blobs managed by the compose creator. It mutates the temp file's current offset via `Seek` before handing it to creators.

## Dependencies And Integration Points

It depends on `TempFile.Stat`, `TempFile.Seek`, GCS object metadata, `gcs.NewCreateObjectRequest`, bucket `CreateObject`, compose object creator, bucket type rapid-write support, component count limits, and chunk retry/transfer timeout settings.

## Risks And Maintenance Notes

Dirty-threshold and unfinalized-object logic is subtle. For unfinalized zonal/rapid objects, size metadata may be stale, so the code bypasses one unchanged-content shortcut to avoid silently skipping truncations. Compose is disabled for rapid-write buckets. Any changes to `TempFile.Stat` semantics can cause missed uploads or redundant uploads. Error wrapping identifies whether failures occurred during stat, seek, create request, or create execution.

## Test Signals

This subset does not include `syncer_test.go`, but the production file has comments documenting expected cases: unmodified temp files return nil object, local-only files upload fully, append-only large finalized objects can use compose, and dirty or unsupported cases upload fully.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/gcsx/syncer_bucket.go

## Scope

This file defines a small adapter combining `gcs.Bucket` and `Syncer` into one value.

## Purpose

`SyncerBucket` lets callers pass around a single object that can be used both for normal bucket operations and for temp-file sync/write-back operations.

## Important APIs, Types, And Functions

- `SyncerBucket` embeds `gcs.Bucket` and `Syncer`.
- `NewSyncerBucket` constructs a `Syncer` with `NewSyncer` and returns both embedded interfaces.

## Control Flow

Construction forwards append threshold, chunk retry deadline, chunk transfer timeout, temporary object prefix, and bucket to `NewSyncer`, then returns `SyncerBucket{bucket, syncer}`.

## State And Persistence Behavior

The adapter has no state beyond embedded interface values. Persistence behavior comes from the wrapped bucket and constructed syncer.

## Dependencies And Integration Points

It depends on the `gcs.Bucket` interface and local `NewSyncer`. It is useful where higher layers need a bucket augmented with write-back sync behavior without changing bucket implementations.

## Risks And Maintenance Notes

Because it uses embedding, method-name collisions between `gcs.Bucket` and `Syncer` could become ambiguous if either interface changes. The adapter inherits all `NewSyncer` behavior, including compose disabling for rapid buckets and temp-object cleanup requirements.

## Test Signals

This file has no direct tests in the listed subset. Coverage is expected through syncer and higher-level bucket integration tests that construct `SyncerBucket`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/syncer_bucket.go -->
