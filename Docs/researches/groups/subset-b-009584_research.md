# subset-b-009584 grouped research

This grouped report covers the source-tree-aligned files assigned to `subset-b-009584`. Each section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader_test.go

Purpose: unit test coverage for the client-side `RangeReader`, the reader that manages a reusable GCS range reader and serves `GCSReaderRequest` buffers from `NewReaderWithReadHandle`.

Important APIs and fixtures: `rangeReaderTest`, `readAt`, `mockNewReaderWithHandleCallForTestBucket`, `blockingReader`, and `countingCloser` drive mocked bucket calls and reader lifecycle assertions. The tests instantiate `NewRangeReader` with noop metrics/tracing and sometimes a filesystem config controlling interrupt propagation.

Control flow and state behavior: tests verify constructor wiring, invariant panics for missing object/bucket/state, `destroy` closing an active reader, range request construction, short reads, EOF handling, and forced reader recreation. Misalignment tests exercise invalidation when cached reader start/limit cannot satisfy a request. Cancellation tests use a blocking reader to confirm context cancellation reaches the active read only while the read is in flight.

Dependencies and integration points: depends on `storage.TestifyMockBucket`, fake readers, `gcs.ReadObjectRequest`, `cfg.Config`, `metrics`, `tracing`, `testify/suite`, and `mock`. It is a direct behavioral signal for `client_readers/range_reader.go`.

Risks and test signals: the suite is strongest around reader reuse, bounds, close behavior, and cancellation. It does not hit real GCS; any transport-specific behavior, metrics labels, or tracing payloads are indirectly checked through fake/mocked readers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/client_readers/range_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator.go

Purpose: implements an append-style `objectCreator` that writes appended bytes to a temporary object and composes the existing source object plus temporary object back over the source object.

Important APIs/types/functions: `newComposeObjectCreator(prefix, bucket)`, `composeObjectCreator`, `chooseName`, and `Create`. `chooseName` reads 64 random bits from `crypto/rand` and formats a temporary object name with the configured prefix. `Create` accepts the existing `srcObject`, optional mtime, upload retry/timeout values, and an `io.Reader` containing appended content.

Control flow: `Create` chooses a temporary name, creates a temp object with `bucket.CreateObject`, defers best-effort deletion of that temp object, copies source metadata, optionally writes `gcs.MtimeMetadataKey`, then calls `bucket.ComposeObjects` with two sources: original object generation and temp object generation. Destination generation and metageneration preconditions preserve source-object consistency.

State and persistence: no local persistent state beyond prefix and bucket. Remote persistent effects are temp object creation, destination compose overwrite, and temp deletion. Temp deletion uses generation `0` to remove the latest temp generation; failures are returned only when compose succeeded.

Dependencies/integration: uses GCS object metadata and precondition semantics, `maps.Copy`, `time.RFC3339Nano`, and wraps `gcs.NotFoundError` from compose as `gcs.PreconditionError` because source clobber is the likely cause.

Risks/test signals: temp cleanup can fail and requires external garbage collection. Source metadata is copied shallowly. NotFound conversion may mask rare temp-object deletion races as source precondition failures. Tests cover temp naming, compose request shape, property preservation, error wrapping, precondition conversion, and cleanup.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator_test.go

Purpose: validates `composeObjectCreator` append behavior against a mocked GCS bucket.

Important APIs and fixtures: `ComposeObjectCreatorTest`, fake source/temp/composed objects, matchers for delete request names, and mock expectations for `CreateObject`, `ComposeObjects`, and `DeleteObject`. The suite uses the project’s jacobsa-style test harness rather than testify.

Control flow and behavior covered: constructor creation, temp object creation request wiring, creation error propagation, compose request construction, destination preconditions, source list ordering, mtime metadata injection, and cleanup. It specifically checks that object metadata and properties such as cache control, content disposition, encoding, content type, custom time, event hold, storage class, and custom metadata are preserved across compose.

State/persistence signals: tests assert that temp object deletion is attempted after compose, and that delete failures surface only after successful compose. They verify the intended remote transaction model: temp create, compose old+temp into destination, delete temp.

Dependencies/integration: depends on `mock_bucket`, `gcs` request/response types, `time`, and error type matching for `gcs.PreconditionError` and `gcs.NotFoundError`.

Risks/test signals: the suite gives strong confidence in request construction and error wrapping, but not in random name uniqueness or real GCS compose semantics. It documents that `NotFoundError` during compose is treated as a precondition error.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/compose_object_creator_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket.go

Purpose: wraps a `gcs.Bucket` so object creation APIs infer a MIME content type from object name extension when the caller did not provide one.

Important APIs/types/functions: `NewContentTypeBucket`, `contentTypeBucket`, and overrides for `CreateObject`, `ComposeObjects`, `CreateObjectChunkWriter`, and `CreateAppendableObjectWriter`.

Control flow: each overridden method checks the incoming request’s `ContentType`. If empty, it calls `mime.TypeByExtension(path.Ext(name))` using `req.Name` or `req.DstName`, mutates the request in place, and forwards it to the embedded bucket.

State and persistence behavior: no stored state beyond the wrapped bucket. It mutates request objects before they hit storage, so downstream calls persist inferred content type metadata on new/composed objects. Explicit content types are preserved.

Dependencies/integration: standard `mime` and `path` packages; `gcs.Bucket` creation and writer interfaces. It composes cleanly with other bucket wrappers because it embeds and delegates to the underlying bucket.

Risks/test signals: request mutation may surprise callers reusing request values. Unknown extensions produce an empty content type, which is passed through. Tests cover create, compose, chunk writer, appendable writer, explicit override preservation, and extension inference.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket_test.go

Purpose: table-driven tests for content-type inference across all creation paths wrapped by `contentTypeBucket`.

Important APIs and fixtures: `contentTypeBucketTestCases` enumerates object names, initially supplied content types, and expected final values. Tests exercise `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, and `ComposeObjects`.

Control flow and behavior covered: each test creates a fake bucket wrapper, sends requests through `NewContentTypeBucket`, and checks the returned object or captured writer request content type. `ComposeObjects` first creates source objects and then composes into a destination to validate destination-name extension inference.

State/persistence signals: confirms the wrapper influences request metadata before storage persists it and does not override an explicit caller-supplied content type. It also covers empty or unknown extensions by expecting the standard library’s extension mapping result.

Dependencies/integration: uses fake storage bucket behavior from internal storage test utilities and the public `gcs` request types.

Risks/test signals: tests cover the wrapper surface broadly, but they are only as complete as Go’s MIME database in the running environment. They do not verify wrapper ordering with other bucket decorators.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/content_type_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader.go

Purpose: implements `FileCacheReader`, a first-layer `Reader` that attempts to satisfy GCS object reads from the local file cache and signals `FallbackToAnotherReader` when GCS should be used.

Important APIs/types/functions: `NewFileCacheReader`, `ReaderName`, `tryReadingFromFileCache`, `ReadAt`, `captureFileCacheMetrics`, `Destroy`, and `CheckInvariants`. State includes the target `MinObject`, `Bucket`, optional `file.CacheHandler`, `cacheFileForRangeRead`, a mutex-protected `file.CacheHandle`, metrics/tracing handles, and FUSE handle ID.

Control flow: `ReadAt` immediately returns EOF for offsets at or beyond object size, then calls `tryReadingFromFileCache`. Cache reads return success when there is a cache hit, a full buffer, or a partial read exactly at object EOF. Otherwise it returns `FallbackToAnotherReader`. `tryReadingFromFileCache` lazily creates a cache handle, handles expected cache misses and exclusions as non-errors, reads through the handle, resets invalid handles, and wraps unexpected cache errors.

State/persistence behavior: it maintains an open cache handle across reads and closes/nils it on invalidation or destroy. The cache handler may start or reuse local download jobs; a read can be write-through where data is fetched from GCS and served from local cache with `cacheHit=false`.

Dependencies/integration: integrates with cache handler/job/lru utilities, metrics, tracing, logger, UUID request logging, and FUSE handle IDs. It relies on cache utility sentinel errors to distinguish fallback from fatal cache failures.

Risks/test signals: concurrency safety depends on correct lock handoff around handle creation and reads. Request offsets below zero are not explicitly rejected here and rely on lower cache layers. Tests cover disabled cache, file-size exclusion, EOF, cache hits/misses, invalid jobs/handles, deleted files, unfinalized objects, destroy races, and concurrent reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader_test.go

Purpose: broad unit coverage for `FileCacheReader` across non-zonal, zonal, and rapid/Pirlo bucket types.

Important APIs and fixtures: `fileCacheReaderTest`, suite variants by bucket type, temp cache directories, `cacheHandler`, mock bucket readers, `mockNewReaderWithHandleCallForTestBucket`, and helper waits for download jobs. It uses fake readers and generated random data to verify actual buffer contents.

Control flow and behavior covered: constructor fields, fallback when cache handler is nil, oversized object cache exclusion, EOF at or beyond object size, cache hits, sequential read reuse, random read behavior with `cacheFileForRangeRead` true/false, transitions from sequential to random, invalid job and invalid file handle recovery, deleted cache file behavior, failed job restart, negative/beyond-size offsets, and destroy.

State/persistence signals: tests observe job-manager state, local cache file deletion, cache handle reuse, invalidation by `InvalidateCache`, and Linux semantics where an open file handle can continue serving data after unlink. Unfinalized object scenarios verify behavior when object size grows relative to cached size.

Dependencies/integration: uses cache file package, cache job manager, storage mocks, fake readers, metrics/tracing noop handles, and `testify/suite`.

Risks/test signals: strong coverage for cache lifecycle and locking, including concurrent `ReadAt` and concurrent `ReadAt` plus `Destroy` without panic. Tests remain local/fake and do not validate filesystem differences outside Linux-style unlink semantics assumed in comments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/file_cache_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/garbage_collect.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/garbage_collect.go

Purpose: deletes stale temporary GCS objects created by append/compose flows under a configured prefix.

Important APIs/functions: `garbageCollectOnce(ctx, tmpObjectPrefix, bucket)` and `garbageCollect(ctx, tmpObjectPrefix, bucket)`.

Control flow: `garbageCollectOnce` creates an `errgroup` pipeline: list all objects with the prefix into a channel, filter objects older than a 30-minute staleness threshold into stale names, then delete each stale object with generation `0`. It increments `objectsDeleted` atomically. `garbageCollect` wakes every 10 minutes until context cancellation and logs success or failure with elapsed time and partial delete count.

State and persistence behavior: no local state. Remote persistent action is deleting latest generations of stale temp objects. Time-based filtering is computed once per run, so objects near threshold are consistently judged for that pass.

Dependencies/integration: uses `storageutil.ListPrefix`, GCS delete requests, `errgroup`, atomic counters, context cancellation, and internal logger. It is intended as cleanup for temporary junk that `composeObjectCreator` may leave behind.

Risks/test signals: delete generation `0` targets latest generation and may delete a newer temp object with the same name if names collide, though names are random. A single delete/list error aborts the run. No test file for this item was listed, so behavior is inferred from implementation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/garbage_collect.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader.go

Purpose: wraps a `gcs.StorageReader` and closes the underlying GCS reader after inactivity, reconnecting later from the last consumed offset with a read handle.

Important APIs/types/functions: `InactiveTimeoutReader`, `ErrZeroInactivityTimeout`, `NewInactiveTimeoutReader`, `NewInactiveTimeoutReaderWithClock`, `createGCSReader`, `Read`, `Close`, `ReadHandle`, `monitor`, `handleTimeout`, and `closeGCSReader`.

Control flow: construction rejects zero timeout, creates an initial reader with `NewReaderWithReadHandle`, derives a cancellable context, and starts a monitor goroutine. `Read` locks, marks active, recreates the GCS reader if timeout closed it, reads, and advances `seen`. The monitor wakes every timeout duration; active readers have `isActive` reset, inactive readers are closed. `Close` cancels the monitor and closes any open reader.

State/persistence behavior: tracks requested byte range, bytes seen, last read handle, active flag, and current reader. It does not persist data locally. Reconnect starts at `reqRange.Start + seen` and preserves the original limit.

Dependencies/integration: uses `gcs.Bucket.NewReaderWithReadHandle`, GCS byte ranges, storage v2 read handles, internal `clock` for tests, `locker`, and logger. It is suitable for many idle range readers while preserving efficient resumability.

Risks/test signals: the monitor closes between one and two timeout durations after last read, by design. Reads after explicit `Close` are unsupported. Locking serializes concurrent reads. Tests cover zero timeout, initial error, timeout close, reconnect success/failure, read handle preservation, close behavior, and a race-style concurrent read/timeout scenario.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader_test.go

Purpose: unit tests for `InactiveTimeoutReader` lifecycle, timeout closure, reconnection, and locking behavior.

Important APIs and fixtures: `InactiveTimeoutReaderTestSuite`, simulated clock, fake storage readers, mock bucket expectations, `setupReader`, and explicit suite teardown that closes remaining readers.

Control flow and behavior covered: initial `NewReaderWithReadHandle` error propagation, zero-timeout rejection, successful initial reads, no close before timeout threshold, `io.ReadFull` success, reconnect failure after timeout, reconnect success with expected offset and stored read handle, explicit close, active-to-inactive timeout transition, nil/non-nil `closeGCSReader`, and concurrent reads while timeout handling runs.

State/persistence signals: tests inspect internal `gcsReader`, `seen`, and `isActive` state, and verify that timeout closure captures the underlying reader’s read handle for the next connection. Reconnect request matching confirms range start advances by bytes already read.

Dependencies/integration: uses `clock.SimulatedClock`, `storage.TestifyMockBucket`, fake readers, `testify/suite`, and GCS request types.

Risks/test signals: tests make timing deterministic through simulated clock except for the race test, which exercises concurrency but cannot prove absence of every race without `go test -race`. They document that explicit close stops the monitor.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/inactive_timeout_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/integration_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/integration_test.go

Purpose: integration-style test suite for higher-level gcsx object mutation, read, sync, append, truncate, and conflict behavior against a bucket-backed test setup.

Important APIs and fixtures: `IntegrationTest`, `SetUp`, `TearDown`, `create`, `objectGeneration`, `sync`, `randBytes`, and registered jacobsa test suite methods such as `ReadThenSync`, `SyncEmptyLocalFile`, `WriteThenSync`, `AppendThenSync`, `TruncateThenSync`, and conflict tests.

Control flow and behavior covered: tests create objects, instantiate local object state, read existing contents, write local content, sync to GCS, verify object generations and contents, and list temporary-object prefixes to ensure no stale temp objects remain. Dirty stat behavior checks size, dirty threshold, and mtime tracking. Conflict tests delete or overwrite backing objects and expect precondition/not-found behavior during sync/read.

State/persistence signals: directly exercises persistent GCS object generations, object contents, local dirty thresholds, local mtime metadata, and remote cleanup of temporary append compose objects. Multiple-interaction scenarios mix reads/writes/truncates/syncs and compare resulting remote content.

Dependencies/integration: depends on the project’s integration harness, bucket fixture, gcs object APIs, local object abstractions outside this file, and `timeutil` matchers.

Risks/test signals: strong end-to-end signal for gcsx semantics, especially generation preconditions and temp cleanup. It may require integration credentials or a fake integration environment and is slower/flakier than pure unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader.go

Purpose: implements a kernel-optimized reader for rapid/zonal buckets using a shared `gcsx.MrdInstance` and multi-range downloader pool.

Important APIs/types/functions: `KernelMRDReader`, `NewKernelMRDReader`, `isShortRead`, `ReaderName`, `CheckInvariants`, `ReadAt`, and `Destroy`. State includes an atomic flag tracking whether the MrdInstance refcount has been incremented, the instance pointer, and metrics handle.

Control flow: empty buffers return immediately. First real read increments the MrdInstance refcount exactly once. Reads delegate to `MrdInstance.Read`, capture parallel GCS read metrics, and retry when `isShortRead` sees bytes fewer than requested plus a gRPC `OutOfRange` error. Retry recreates the MRD pool if possible, then reads the remaining buffer from the advanced offset. `Destroy` decrements refcount if in use and nils the instance.

State/persistence behavior: does not store data; manages MrdInstance lifecycle through refcount. Short-read recovery updates remote connection state by recreating MRD, not object metadata.

Dependencies/integration: integrates with `gcsx.Reader`, `MrdInstance`, metrics, gRPC status/codes, and logger. It is selected by `NewKernelReader` for rapid buckets.

Risks/test signals: assumes `Destroy` only runs after active reads finish. If MRD recreation fails, retry continues with the older MRD. Tests cover empty/nil/success/multiple reads, short-read classification, retry behavior, destroy refcounting, and context cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader_test.go

Purpose: validates `KernelMRDReader` and its short-read retry logic over fake MRD instances.

Important APIs and fixtures: `KernelMRDReaderTest`, configured `MrdInstance`, fake multi-range downloaders, mock bucket calls, and table tests for `isShortRead`.

Control flow and behavior covered: constructor fields, empty-buffer fast path, normal read, multiple reads reusing one MRD pool, nil instance error, short reads that should not retry, gRPC OutOfRange short reads that recreate MRD and retry remaining data, retry failures, recreation failure fallback to old MRD, destroy after use, destroy before read, and context cancellation propagation.

State/persistence signals: tests check MrdInstance refcount transitions, reuse of the same pool across multiple reads, and recreation calls through `NewMultiRangeDownloader`. Short-read tests verify final byte counts combine first attempt and retry.

Dependencies/integration: uses internal fake MRDs, `storage.TestifyMockBucket`, `cfg.Config`, noop metrics, gRPC `status.Error`, and `testify/suite`.

Risks/test signals: strong unit coverage for rapid bucket reader behavior, but not kernel read-ahead itself. Concurrent reads are not directly stressed in this file.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_mrd_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader.go

Purpose: implements a kernel-optimized range reader for standard/regional buckets, creating a fresh GCS range reader for every request.

Important APIs/types/functions: `KernelRangeReader`, `NewKernelRangeReader`, `CheckInvariants`, `ReadAt`, `Destroy`, and `ReaderName`.

Control flow: `CheckInvariants` panics if bucket or instance is nil. `ReadAt` fetches the current `MinObject` from `KernelRangeReaderInstance`, returns an error if nil, returns EOF for offsets at/after object size, caps end offset at object size, opens a reader with `NewReaderWithReadHandle`, `io.ReadFull`s the exact bounded slice, defers close with warning on close error, and captures parallel read metrics.

State/persistence behavior: stateless aside from bucket, instance, and metrics. It reads remote data but does not cache or persist local state. Current object generation/size come from the shared instance, allowing updates after sync or mutation.

Dependencies/integration: depends on `gcsx.Reader`, GCS byte ranges, storage reader close semantics, logger, and metrics. It is selected by `NewKernelReader` for non-rapid buckets.

Risks/test signals: every read creates a new connection, trading simplicity for per-read overhead. Partial reads return `io.ErrUnexpectedEOF` from `io.ReadFull` if the storage reader under-delivers. Tests cover success, EOF, partial object-size capping, new-reader errors, nil object, name, and constructor.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_instance.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_instance.go

Purpose: provides a small thread-safe holder for the latest `gcs.MinObject` used by `KernelRangeReader`.

Important APIs/types/functions: `KernelRangeReaderInstance`, `NewKernelRangeReaderInstance`, `SetMinObject`, and `GetMinObject`.

Control flow: construction stores the initial object. `SetMinObject` takes a write lock and replaces the pointer. `GetMinObject` takes a read lock and returns the stored pointer.

State/persistence behavior: state is in memory only and represents current object metadata such as name, generation, size, and content encoding. There is no copy-on-read despite the comment saying “copy”; callers receive the pointer currently held.

Dependencies/integration: depends only on `sync.RWMutex` and `gcs.MinObject`. Used by kernel range readers and factory wiring for standard buckets.

Risks/test signals: pointer return means callers could mutate the object without locking if they hold the pointer. No dedicated test file is listed for this instance; factory and range-reader tests indirectly exercise it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_instance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_test.go

Purpose: unit tests for `KernelRangeReader` standard/regional bucket behavior.

Important APIs and fixtures: `KernelRangeReaderTest`, `mockStorageReader` implementing `ReadHandle`, mock bucket expectations, and `KernelRangeReaderInstance` setup.

Control flow and behavior covered: constructor field wiring, reader name, successful read into buffer, EOF when offset equals/over object size, partial reads capped to object size, error wrapping when creating the storage reader fails, and nil object error when the instance has no current object.

State/persistence signals: tests validate that current object size controls range limits and that a fresh storage reader is requested per read. They do not mutate the instance concurrently.

Dependencies/integration: uses `storage.TestifyMockBucket`, fake `io.NopCloser` readers, noop metrics, `testify/suite`, and GCS request types.

Risks/test signals: it confirms behavior at API boundaries but does not assert the exact request matcher for every range field in all tests. It also does not cover close errors or invariant panics.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_range_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory.go

Purpose: chooses the kernel-optimized reader implementation based on bucket type.

Important API: `NewKernelReader(bucket, kernelRangeReaderInstance, mrdInstance, metricsHandle) gcsx.Reader`.

Control flow: calls `bucket.BucketType().IsRapid()`. Rapid/zonal buckets receive `NewKernelMRDReader(mrdInstance, metricsHandle)` for MRD-backed parallel reads. Other buckets receive `NewKernelRangeReader(bucket, kernelRangeReaderInstance, metricsHandle)` for per-request range reads.

State/persistence behavior: the factory owns no persistent state and simply wires the correct reader with shared instances supplied by higher layers.

Dependencies/integration: integrates `gcs.BucketType`, `gcsx.MrdInstance`, `KernelRangeReaderInstance`, metrics, and the `gcsx.Reader` interface. It is the selection point that aligns kernel read path with storage backend capabilities.

Risks/test signals: if bucket type classification changes, this factory controls behavior. It does not validate nil arguments; selected reader may error/panic later depending on use. Tests cover rapid and standard selection.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory_test.go

Purpose: verifies `NewKernelReader` dispatches to the expected concrete reader for rapid versus standard buckets.

Important APIs and fixtures: two tests create a `storage.TestifyMockBucket`, configure `BucketType`, call `NewKernelReader`, and assert returned concrete type.

Control flow and behavior covered: `TestNewKernelReader_Zonal` expects `*KernelMRDReader` when `BucketType{Zonal: true}`. `TestNewKernelReader_Standard` expects `*KernelRangeReader` when `Zonal` is false.

State/persistence signals: no persistence. Tests validate factory wiring only.

Dependencies/integration: uses mock bucket and `gcs.BucketType`. It intentionally passes nil reader instances/metrics because construction, not read behavior, is under test.

Risks/test signals: narrow but high-signal coverage for branch selection. It does not check other `BucketType` fields beyond `Zonal`/rapid behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/kernel_readers/kernel_reader_factory_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mock_random_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mock_random_reader.go

Purpose: provides a testify mock implementation of the `RandomReader` interface for unit tests.

Important APIs/types/functions: `MockRandomReader` embeds `RandomReader` and `mock.Mock`; methods `ReadAt`, `Object`, `Destroy`, and `CheckInvariants` delegate to `m.Called(...)`.

Control flow: each method records or retrieves mocked expectations. `ReadAt` returns `args.Get(0).(ObjectData)` and `args.Error(1)`. `Object` returns `*gcs.MinObject`.

State/persistence behavior: no production state or persistence. Test state lives in testify’s mock expectation/call ledger.

Dependencies/integration: depends on `context`, `gcs.MinObject`, `ObjectData`, `RandomReader`, and `github.com/stretchr/testify/mock`. It supports tests for components that depend on random reader behavior without touching real storage.

Risks/test signals: type assertions will panic if a test configures return values with the wrong type. Because it embeds the interface, missing mocked methods may be satisfied by embedded nil interface behavior only if not called.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mock_random_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mock_reader.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mock_reader.go

Purpose: provides a testify mock implementation of the generic `Reader` interface.

Important APIs/types/functions: `MockReader`, `ReaderName`, `ReadAt`, `Destroy`, and `CheckInvariants`.

Control flow: `ReaderName` returns the fixed string `mock_reader`. `ReadAt` delegates to testify expectations using the context and `*ReadRequest`, returning a `ReadResponse` and error. Lifecycle methods record expectation calls.

State/persistence behavior: no production state or persistence. All behavior is driven by mock expectations in tests.

Dependencies/integration: depends on `context`, `ReadRequest`, `ReadResponse`, and testify `mock`. Used by read-manager or wrapper tests needing a controllable `gcsx.Reader`.

Risks/test signals: incorrect return types in test setup panic due to type assertion. The fixed reader name is useful for assertions but may mask production-specific names in tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mock_reader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance.go

Purpose: manages an MRD pool for one file inode, including lazy pool creation, generation-aware pool replacement, reads, refcounting, inactive LRU caching, eviction, and destruction.

Important APIs/types/functions: `MrdInstance`, `NewMrdInstance`, `SetMinObject`, `GetMinObject`, `getMRDEntry`, `Read`, `ensureMRDPool`, `RecreateMRD`, `closePool`, `closePoolWithTimeout`, `Destroy`, `getKey`, `IncrementRefCount`, `DecrementRefCount`, `handleEviction`, `Size`, and `RefCount`.

Control flow: reads lazily ensure a pool, get the next valid entry, recreate invalid entries, issue `mrd.Add` into a bytes buffer backed by the caller buffer, and wait for callback or context cancellation depending on `IgnoreInterrupts`. Object generation changes in `SetMinObject` swap in a new pool; same generation only updates metadata. Refcount zero inserts the instance into an LRU cache, and evicted inactive instances close pools outside locks.

State/persistence behavior: in-memory state includes object metadata, bucket, MRD pool pointer, refcount, inode ID, cache, and config. It does not persist data locally, but maintains remote read handles within MRD pools. Pool closing is asynchronous with a 120-second warning timeout.

Dependencies/integration: integrates `MRDPool`, LRU cache, config, logger, monitor metrics, GCS bucket/MRD APIs, and FUSE inode IDs. `KernelMRDReader` uses it for rapid bucket reads.

Risks/test signals: lock ordering is important across refcount, cache, and pool locks. `Destroy` warns if active users remain. Asynchronous close may delay resource release. Tests cover creation, reads, invalid entry recreation, cancellation, refcount/LRU races, generation swap, timeout logging, and error paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance_test.go

Purpose: comprehensive unit tests for `MrdInstance` read, pool, refcount, cache, eviction, and generation-update behavior.

Important APIs and fixtures: `MrdInstanceTest`, mock bucket, fake MRDs, LRU cache, config with MRD pool size, and log capture helpers for timeout warning verification.

Control flow and behavior covered: constructor fields, successful reads, lazy pool initialization, invalid MRD recreation, ensure/recreation failures, empty buffer, context cancellation, MRD add errors, `getMRDEntry`, `RecreateMRD`, `Destroy`, refcount increment/decrement, cache insertion/removal, eviction behavior, key formatting, pool size reporting, cache insert failure, `closePool`, eviction races, `createAndSwapPool`, nil/same/different generation `SetMinObject`, and `GetMinObject`.

State/persistence signals: tests inspect `mrdPool`, refcount, cache membership, object generation updates, and asynchronous close timeout logging. They validate reopening removes an instance from inactive cache and preserves pool reuse when safe.

Dependencies/integration: uses storage mock bucket, fake MRDs, LRU cache package, config, logger capture, and `testify/suite`.

Risks/test signals: strong coverage for lock-sensitive lifecycle paths, including resurrected and re-added cache entries. Some close behavior is asynchronous and verified with sleeps, so timing can be a residual flake risk.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_instance_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool.go

Purpose: manages a round-robin pool of `gcs.MultiRangeDownloader` instances for concurrent reads of one GCS object.

Important APIs/types/functions: `MRDEntry`, `MRDPoolConfig`, `MRDPool`, `determinePoolSize`, `NewMRDPool`, `createRemainingMRDs`, `Next`, `RecreateMRD`, `Close`, and `Size`.

Control flow: pool size is reduced to 1 for objects below 100 MiB and 2 for objects below 500 MiB, otherwise configured size remains. `NewMRDPool` creates the first downloader synchronously, maps initial `NotFoundError` to `FileClobberedError`, stores current size, and creates remaining downloaders asynchronously using the first downloader’s handle. `Next` round-robins over initialized entries. `RecreateMRD` locks one entry and obtains a handle from that entry, fallback handle, or a peer via `TryRLock`. `Close` stops background creation, waits for it, waits for in-flight downloads, captures a handle, closes downloaders, and nils entries.

State/persistence behavior: in-memory entries, atomics for next/current size, background creation control channel, and wait group. It maintains remote read handles but no local data.

Dependencies/integration: GCS MRD API, file-clobbered error type, logger, atomics, and sync primitives. Used by `MrdInstance`.

Risks/test signals: if asynchronous creation fails, `currentSize` still increases, leaving nil entries that callers must recreate. Closing `stopCreation` twice would panic, so `Close` should be single-use. Tests cover sizing, async creation failure, file clobber, round robin, handle selection, recreation errors, close semantics, and context non-cancellation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool_test.go

Purpose: unit tests for `MRDPool` construction, sizing, round-robin selection, recreation, and close behavior.

Important APIs and fixtures: `mrdPoolTest`, `MRDPoolConfig`, mock bucket, fake MRDs with handles, and table-driven pool-size cases.

Control flow and behavior covered: small and large file initialization, async creation failure tolerance, file-clobbered conversion for initial not-found, nil config error, generic creation error, `Next` round-robin over initialized entries, size determination thresholds, `RecreateMRD` using current, fallback, or peer handles, recreate failure, `Close` waiting/closing entries and returning a handle, and verifying `Close` does not cancel the downloader creation context.

State/persistence signals: tests inspect `entries`, `currentSize`, `current`, downloader handles, and niling after close. Async creation tests wait for creation goroutines to complete before assertions.

Dependencies/integration: uses storage mock bucket, fake multi-range downloaders, `testify/suite`, and GCS request matchers.

Risks/test signals: good unit coverage for pool mechanics. It does not deeply stress concurrent `Next` and `RecreateMRD`, but implementation uses atomics and entry locks for that path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/mrd_pool_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper.go

Purpose: wraps a single `gcs.MultiRangeDownloader` with lazy creation, read helper logic, refcounting, optional LRU caching, handle reuse, and eviction cleanup.

Important APIs/types/functions: `NewMultiRangeDownloaderWrapper`, `readResult`, `MultiRangeDownloaderWrapper`, `SetMinObject`, `wrapperKey`, `GetMinObject`, `GetRefCount`, `IncrementRefCount`, `DecrementRefCount`, `CloseMRDForEviction`, `ensureMultiRangeDownloader`, `Read`, `closeLocked`, and `Size`.

Control flow: construction requires non-nil object. Refcount increment removes an inactive wrapper from cache. Decrement inserts into cache at zero and closes evicted wrappers outside the current lock. `ensureMultiRangeDownloader` handles nil/unusable/forced recreation by temporarily upgrading from read lock to write lock, using existing or cached handles unless force recreation is requested, and mapping `NotFoundError` to `FileClobberedError`. `Read` creates/reuses MRD, caps end offset to buffer length, issues `Add`, waits for callback or context depending on `IgnoreInterrupts`, wraps non-EOF errors, and captures metrics.

State/persistence behavior: stores object/bucket/config, wrapped downloader, cached read handle, refcount, and LRU cache pointer. No local data persistence; remote read handle is preserved on close for future recreation.

Dependencies/integration: GCS MRD APIs, LRU cache, config, tracing propagation, monitor metrics, logger, and file-clobbered error type. It supports client-side multi-range reader flows distinct from pooled `MrdInstance`.

Risks/test signals: the callback channel is closed via a mutex to avoid sends after cancellation, but complexity is high. Refcount misuse returns errors. Cache eviction race protection checks refcount and cache membership. Tests cover parallel refcounts, reads, cancellation modes, EOF/error wrapping, recreation, file clobber, cache reuse/eviction/races, and disabled cache behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper_test.go -->
## sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper_test.go

Purpose: comprehensive tests for `MultiRangeDownloaderWrapper` read behavior, downloader creation/recreation, refcounting, and LRU cache lifecycle.

Important APIs and fixtures: `mrdWrapperTest`, `mrdWrapperCacheTest`, mock bucket, fake multi-range downloaders with sleeps/errors, generated object data, and cache capacity variants.

Control flow and behavior covered: parallel refcount increments/decrements, invalid decrement, successful reads, MRD creation errors, short reads, cancellation with interrupts enabled versus disabled, EOF passthrough, non-EOF error wrapping, constructor validation, `SetMinObject`, ensure behavior for missing fields, reusable existing MRD, unusable existing MRD recreation, force recreation, file-clobbered conversion, cache add/remove, cache eviction on overflow, deleted-if-reopened behavior, concurrent add/remove, disabled cache, eviction/repool races, and multiple evictions.

State/persistence signals: tests inspect refcount, `Wrapped`, cached handle reuse, LRU membership, cache size, and whether MRDs remain open or are closed after eviction. They validate that cached wrappers are removed on reopen and that inactive evicted wrappers close safely.

Dependencies/integration: uses storage mock bucket, fake MRDs, LRU cache, config with `IgnoreInterrupts`, `testify/suite`, and request matching.

Risks/test signals: strong local concurrency and lifecycle coverage. Real network callback timing and production tracing are not validated, but fake downloader sleep/error modes exercise the key asynchronous paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/gcsx/multi_range_downloader_wrapper_test.go -->
