# Research Group subset-b-009587

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket_test.go

## Purpose
`fast_stat_bucket_test.go` is the main unit-test suite for the caching `FastStatBucket` wrapper. It verifies that the wrapper uses `metadata.StatCache` as a positive and negative metadata cache while delegating actual object and folder operations to an underlying `gcs.Bucket`.

## Important APIs, Types, and Functions
The shared fixture `fastStatBucketTest` constructs a simulated clock, `mock_gcscaching.MockStatCache`, mocked wrapped bucket, and `caching.NewFastStatBucket(primaryCacheTTL, cache, clock, wrapped, negativeCacheTTL, isTypeCacheDeprecated, isImplicitDir)`. Test suites cover object creation, resumable and appendable writers, upload finalization, pending-write flush, copy, compose, stat, list, update, delete, folder APIs, move, reader construction, and multi-range downloader construction.

The stat-related tests exercise `gcs.StatObjectRequest` fields including `ForceFetchFromGcs`, `ReturnExtendedObjectAttributes`, and `FetchOnlyFromCache`. Folder tests exercise `GetFolderRequest.FetchOnlyFromCache`. Listing tests validate cache insertion for `MinObjects`, collapsed runs, implicit directories, and hierarchical namespace buckets.

## Control Flow
Mutation operations generally expect cache invalidation before calling the wrapped bucket. `CreateObject`, `FinalizeUpload`, `FlushPendingWrites`, `CopyObject`, `ComposeObjects`, `UpdateObject`, `CreateFolder`, `RenameFolder`, and `MoveObject` erase stale entries, delegate, and insert successful returned metadata into cache with `clock.Now().Add(primaryCacheTTL)`. Failure paths usually return the wrapped error without positive insertion; precondition and not-found paths are checked so stale entries are not retained incorrectly.

`StatObject` first consults `LookUp` unless `ForceFetchFromGcs` bypasses the cache. A positive hit returns the cached `MinObject`, a cached nil means a negative hit and returns `gcs.NotFoundError`, and a miss delegates to the wrapped bucket. Wrapped not-found responses add a negative cache entry expiring at `negativeCacheTTL`; wrapped success inserts a positive entry. The test also asserts that requesting extended attributes without forcing a GCS fetch panics, because the cache cannot supply the extended attribute surface.

`ListObjects` delegates first, then inserts listed objects and derived directory entries unless the context has already been cancelled. Flat buckets cache implicit directories from prefixes, object paths, and collapsed runs when implicit-dir caching is enabled. HNS buckets cache real folder entries differently, using `InsertFolder` for collapsed folder results. Reader and multi-range downloader creation do not use cache for success, but a wrapped `NotFoundError` erases the object entry to remove stale positive metadata.

## State and Persistence Behavior
The tests are memory-only but model time-based cache state with `timeutil.SimulatedClock`. They assert expiration timestamps rather than sleeping. The wrapper state under test is the stat cache: object positive entries, object negative entries, folder positive entries, folder negative entries, implicit directory entries, and prefix-wide erasure for folder rename. There is no durable persistence in this file.

## Dependencies and Integration Points
The file depends on `caching.NewFastStatBucket`, `metadata.StatCache` through a generated oglemock mock, the storage `MockBucket`, `gcs` request/response types, `storage.ObjectWriter`, `fake.FakeReader`, and ogletest/oglemock matchers. It integrates indirectly with the cache implementation by treating `StatCache` as an interaction contract.

## Risks and Edge Cases
The highest-risk areas are invalidation ordering around mutations, negative-cache invalidation after create/list/update, and not caching partial/list results when context cancellation is already visible. Extended object attributes are deliberately unavailable from cache; code paths that set `ReturnExtendedObjectAttributes` without `ForceFetchFromGcs` are expected to panic. HNS folder entries and flat implicit directories have different cache insertion semantics, so regressions can appear only for one bucket type.

## Test Signals
This file itself is a broad test signal. It covers happy paths and failures for wrapped bucket calls, TTL computation, positive/negative object cache hits, cache-only stat/folder misses returning `caching.CacheMissError`, folder CRUD caching, move invalidation of both source and destination, reader/downloader stale-cache removal on not-found, and cancelled-listing suppression of cache updates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/fast_stat_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/integration_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/caching/integration_test.go

## Purpose
`integration_test.go` verifies `FastStatBucket` behavior with a real in-memory stat cache and a fake bucket rather than strict mocks. It checks observable caching semantics across object create, stat, list, update, positive TTL expiration, negative TTL expiration, and negative-cache invalidation.

## Important APIs, Types, and Functions
`IntegrationTest.SetUp` creates an LRU cache sized with `cfg.AverageSizeOfPositiveStatCacheEntry`, wraps it with `metadata.NewStatCacheBucketView`, constructs `fake.NewFakeBucket`, and wraps the fake bucket with `caching.NewFastStatBucket`. The helper `stat` calls `bucket.StatObject` and converts the returned `MinObject` to a full object with `storageutil.ConvertMinObjectToObject`.

## Control Flow
Each test performs operations through both the caching bucket and the wrapped fake bucket. Back-door operations against `t.wrapped` simulate GCS changing outside the cache wrapper. Positive-cache tests create, stat, list, or update through the cache wrapper, delete the real object through the back door, then verify stat still returns the cached object until TTL expiry. Negative-cache tests stat a missing object to cache not-found, create the object through the back door, then verify the object remains hidden until a cache invalidating operation or negative TTL expiry occurs.

## State and Persistence Behavior
All state is in-memory: the fake bucket owns object records and the LRU-backed stat cache owns cached metadata. A simulated clock controls both primary and negative TTL checks. The tests intentionally separate cache state from underlying bucket state to prove staleness is allowed within configured TTL windows.

## Dependencies and Integration Points
The file integrates `cfg`, `cache/lru`, `cache/metadata`, `caching`, `fake`, `gcs`, `storageutil`, ogletest matchers, and `timeutil.SimulatedClock`. It is the bridge between unit-level interaction tests and the actual metadata cache implementation.

## Risks and Edge Cases
The tests encode the intended staleness contract: cache may return deleted objects until positive TTL expiry and may hide newly created objects until negative TTL expiry unless a wrapper-observed create/list/update invalidates the entry. If product expectations change toward stronger consistency, these tests will need revision. They do not cover HNS folder cache behavior or cancelled contexts; those are in `fast_stat_bucket_test.go`.

## Test Signals
Coverage includes positive insertion from create/stat/list/update, positive expiration, negative insertion from stat not-found, create/list/update invalidating negative entries, and negative expiration. Because it uses real cache and fake bucket implementations, it catches integration mistakes that pure oglemock call-order tests can miss.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/integration_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/mock_gcscaching/mock_stat_cache.go -->
# sources/user-network-fs/gcsfuse/internal/storage/caching/mock_gcscaching/mock_stat_cache.go

## Purpose
`mock_stat_cache.go` is an auto-generated oglemock implementation of the `metadata.StatCache` interface for caching tests. It lets tests assert precise interactions between `FastStatBucket` and the cache without depending on the concrete cache implementation.

## Important APIs, Types, and Functions
`MockStatCache` embeds `metadata.StatCache` and `oglemock.MockObject`. `NewMockStatCache` returns a `mockStatCache` bound to an oglemock controller and description. The mock implements `AddNegativeEntry`, `AddNegativeEntryForFolder`, `Erase`, `Insert`, `LookUp`, `InsertFolder`, `LookUpFolder`, `EraseEntriesWithGivenPrefix`, and `InsertImplicitDir`, plus `Oglemock_Id` and `Oglemock_Description`.

## Control Flow
Every mocked method captures caller file and line with `runtime.Caller`, forwards method name and arguments to `controller.HandleMethodCall`, validates return arity, and type-asserts returned values for lookup methods. Methods that should not return values panic if the controller provides any. `LookUp` returns `(bool, *gcs.MinObject)` and `LookUpFolder` returns `(bool, *gcs.Folder)`.

## State and Persistence Behavior
The mock stores only the oglemock controller pointer and description. Expectations, call history, and configured return values live in the controller. There is no cache state or durable persistence here.

## Dependencies and Integration Points
The file depends on `metadata.StatCache`, `gcs` metadata types, `oglemock`, `runtime`, `time`, and `unsafe`. It is used by `fast_stat_bucket_test.go` to check cache interactions such as erase-before-delegate, positive insert TTLs, negative insert TTLs, folder lookup, and implicit directory insertion.

## Risks and Edge Cases
This generated mock must stay in sync with `metadata.StatCache`. Interface method additions or signature changes will fail compilation until regenerated. The panic messages have minor naming inconsistencies, but those do not affect normal tests. Type assertions in lookup return handling mean tests must return exactly the expected pointer types.

## Test Signals
There are no direct tests for the mock; compile-time conformance and heavy use in cache tests are the validation signal. Failures generally indicate either stale generated code or incorrect expectations in `FastStatBucket` unit tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/caching/mock_gcscaching/mock_stat_cache.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper.go -->
# sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper.go

## Purpose
`control_client_wrapper.go` defines the local abstraction and wrappers for Google Cloud Storage Control API calls used by gcsfuse. It adds billing-project metadata, gcsfuse-level retry behavior, and raw gax retry options for folder APIs.

## Important APIs, Types, and Functions
`StorageControlClient` is the narrow interface for `GetStorageLayout`, `DeleteFolder`, `GetFolder`, `RenameFolder`, and `CreateFolder`. `storageControlClientWithBillingProject` wraps a client and appends `x-goog-user-project` metadata to most calls. `storageControlClientWithRetry` wraps a client with `storageutil.RetryConfig` and flags that control whether retries apply only to storage layout or to all folder APIs too.

Factory helpers are `withBillingProject`, `newRetryWrapper`, `withRetryOnAllAPIs`, and `withRetryOnStorageLayout`. `storageControlClientGaxRetryOptions` builds gax timeout/retry call options. `addGaxRetriesForFolderAPIs` mutates a raw `control.StorageControlClient` call-options struct to apply retries to folder operations.

## Control Flow
Billing-project wrapping appends outgoing gRPC metadata for `GetStorageLayout`, `DeleteFolder`, `GetFolder`, and `CreateFolder`; `RenameFolder` intentionally uses the original context because the long-running operation path does not support that billing header.

Retry wrapping checks enable flags per method. If disabled, it directly delegates. If enabled, it builds an attempt closure that calls the raw client with an attempt context and passes it to `storageutil.ExecuteWithRetry` or `ExecuteWithRetryAtLogLevel`. Request descriptions use bucket/folder names and are included in retry logging/error context. `newRetryWrapper` unwraps an existing retry wrapper before constructing a new one to avoid nested retry loops.

Gax retry options apply `DefaultTotalRetryBudget` as timeout and retry on `ResourceExhausted`, `Unavailable`, `DeadlineExceeded`, `Internal`, `Unknown`, and temporarily `Unauthenticated`. Folder gax retries are installed in place after validating both raw client and client config are non-nil and `CallOptions` is initialized.

## State and Persistence Behavior
The wrappers are lightweight in-memory decorators. They retain a raw client pointer, billing-project string, retry config pointer, and retry-enable booleans. No state is persisted, but retry behavior affects timing, call repetition, and context cancellation.

## Dependencies and Integration Points
The code depends on `cloud.google.com/go/storage/control/apiv2`, generated `controlpb` messages, `gax`, gRPC status codes, `metadata.AppendToOutgoingContext`, `logger`, and `storageutil` retry configuration. It integrates with bucket construction code that needs HNS storage layout and folder APIs.

## Risks and Edge Cases
Retry policy correctness is the key risk. Retrying non-idempotent or long-running folder operations can duplicate requests if server semantics are not safe; this is gated by `retryFolderAPIs` and gax configuration. `RenameFolder` omits the billing project by design, which can surprise callers expecting all API calls to carry it. `addGaxRetriesForFolderAPIs` resets the whole call-options struct, so future call options could be accidentally cleared. Including `Unauthenticated` as retryable is marked temporary and should be revisited.

## Test Signals
`control_client_wrapper_test.go` covers success, retryable error recovery, non-retryable errors, timeout behavior, methods that should not retry in storage-layout-only mode, wrapper unnesting, gax option shape, unauthenticated retryability, and invalid raw-client inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper_test.go

## Purpose
`control_client_wrapper_test.go` validates gcsfuse's Storage Control client wrappers. It verifies timeout-driven retry behavior, retryable versus non-retryable gRPC errors, storage-layout-only versus all-API retry modes, wrapper unnesting, and gax retry option installation.

## Important APIs, Types, and Functions
`stallingStorageControlClient` wraps a `StorageControlClient` and optionally delays `GetStorageLayout` and folder APIs until either a timer fires or the attempt context is cancelled. `ControlClientRetryWrapperTest`, `StorageLayoutRetryWrapperTest`, and `AllApiRetryWrapperTest` are testify suites around a `MockStorageControlClient`. `newHelperRetryWrapper` constructs a `newRetryWrapper` with small deadlines/backoffs to keep tests fast.

The gax-specific suite `ControlClientGaxRetryWrapperTest` checks `storageControlClientGaxRetryOptions` and `addGaxRetriesForFolderAPIs`.

## Control Flow
Storage-layout-only tests create a retry wrapper with folder retries disabled. They assert `GetStorageLayout` succeeds on first attempt, retries an `Unavailable` error then succeeds, wraps non-retryable `NotFound`, and times out without calling the raw client when the stalling layer exceeds per-attempt deadline. The same suite asserts folder APIs delegate directly and return a single retryable error without retry.

All-API tests repeat storage layout cases and then exercise `DeleteFolder`, `GetFolder`, `RenameFolder`, and `CreateFolder` for first-attempt success, retryable-error-then-success, non-retryable errors, and timeout. Wrapper factory tests assert `withRetryOnStorageLayout` and `withRetryOnAllAPIs` produce `*storageControlClientWithRetry`, set the right booleans, and unwrap an already wrapped client rather than nesting.

Gax tests resolve the returned `gax.CallOption`s to confirm retry settings exist and `codes.Unauthenticated` is currently treated as retryable. They also check nil input errors and that folder APIs receive two gax options while `GetStorageLayout` remains untouched by `addGaxRetriesForFolderAPIs`.

## State and Persistence Behavior
The test state is per-suite and in-memory: mock expectations, context, configured stall durations, and retry timing parameters. The tests depend on microsecond-scale timing, but there is no persistent state.

## Dependencies and Integration Points
The file depends on generated control protobufs, `control.RenameFolderOperation`, `gax`, `storageutil`, gRPC codes/status, testify assert/require/mock/suite, and the generated `MockStorageControlClient`. It directly validates the public helper behavior used during storage client setup.

## Risks and Edge Cases
Microsecond retry deadlines can be sensitive to scheduler delays; the tests avoid exact attempt counts in timeout cases and assert context deadline behavior. The helper method accepts a `controlClient` parameter but returns `newRetryWrapper(t.stallingClient, ...)`, so the suite is coupled to fixture state. The tests cover retry shape but not billing-project metadata wrapping.

## Test Signals
The file is the primary test signal for `control_client_wrapper.go`. It covers retry gating, retryable status handling, non-retryable error formatting, timeout cancellation before raw calls, all four folder APIs, unwrapping nested retry clients, gax option creation, unauthenticated retryability, and invalid gax-installation inputs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/control_client_wrapper_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/debug_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/debug_bucket.go

## Purpose
`debug_bucket.go` implements a logging decorator for `gcs.Bucket`. It traces bucket operations, request IDs, durations, errors, upload progress callbacks, reader close timing, and multi-range downloader activity while preserving the wrapped bucket behavior.

## Important APIs, Types, and Functions
`NewDebugBucket` returns a `debugBucket` around a wrapped bucket. `debugBucket` stores the wrapped `gcs.Bucket` and an atomic `nextRequestID`. Helper methods `mintRequestID`, `requestLogf`, `startRequest`, and `finishRequest` produce trace logs. `debugReader` wraps `gcs.StorageReader` to log read errors and final close status. `debugMultiRangeDownloader` wraps `gcs.MultiRangeDownloader` to trace `Add`, `Close`, `Wait`, and `GetHandle`.

The bucket implementation forwards `Name`, `BucketType`, `NewReaderWithReadHandle`, create/write/finalize/flush, copy/compose/stat/list/update/delete/move, folder operations, `NewMultiRangeDownloader`, and `GCSName`.

## Control Flow
Each operation starts by minting a request ID, formatting a human-readable description, and logging an incoming line. Most methods defer `finishRequest` so duration and final error are logged. Reader creation logs the request immediately; if creating the wrapped reader fails, it logs completion at once, otherwise it returns `debugReader`, which delays final completion logging until `Close`. Upload methods install a default progress callback when the caller did not provide one.

Multi-range downloader creation logs the constructor and wraps the returned downloader. Each `Add` call logs a separate range request and wraps the callback so completion is logged when the underlying range finishes. `Wait` and `Close` are also traced. `Error` delegates without logging; `GetHandle` logs as an operation.

## State and Persistence Behavior
The only internal state is the monotonically increasing request ID counter. The wrapper has no durable persistence and does not mutate bucket data except by delegating to the wrapped bucket. Side effects are trace logs and default progress callbacks added to request structs.

## Dependencies and Integration Points
The file depends on `logger.Tracef`, `gcs` interfaces and request types, `cloud.google.com/go/storage` read handles, `io`, `sync/atomic`, `time`, and `context`. It can be layered around any `gcs.Bucket`, including fake, cached, or real buckets, to diagnose storage behavior.

## Risks and Edge Cases
Because progress callbacks may be written into caller-provided request structs, callers reusing requests can observe the mutation. Request descriptions include object and folder names, so trace logs can contain user data. `setupReader` always calls `NewReaderWithReadHandle`; if future bucket interfaces distinguish reader methods, this wrapper must be updated. Multi-range `Add` logs completion only when callbacks run; if an implementation never invokes callbacks, those request logs remain unfinished.

## Test Signals
There are no direct tests in this subset. Compile-time conformance to `gcs.Bucket` and behavior observed through higher-level storage tests are the main signals. Useful tests would assert wrapped delegation, request ID uniqueness under concurrency, reader close logging, callback preservation, and nil-callback progress logging.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/debug_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket.go

## Purpose
`dummy_io_bucket.go` implements a `gcs.Bucket` wrapper that avoids real object-content reads and instead serves zero-filled data with configurable latency. It is useful for dummy IO or performance paths where metadata and write operations still delegate to a real bucket, but data reads should not contact GCS.

## Important APIs, Types, and Functions
`DummyIOBucketParams` carries `ReaderLatency` and `PerMBLatency`. `NewDummyIOBucket` returns nil for nil wrapped buckets or a `dummyIOBucket`. The wrapper delegates metadata, writes, object mutations, folder operations, and naming to the wrapped bucket. `NewReaderWithReadHandle` returns a `dummyReader` for explicit byte ranges. `NewMultiRangeDownloader` returns a `dummyMultiRangeDownloader`.

`calculateLatency` converts bytes and per-MB latency to a duration. `dummyReader` implements `gcs.StorageReader` with total length, bytes read, non-nil read handle, and per-MB latency. `dummyMultiRangeDownloader` uses a wait group and writes zeros to requested outputs asynchronously. `zeroReader` is an infinite zero-producing `io.Reader`.

## Control Flow
`NewReaderWithReadHandle` rejects nil ranges and invalid ranges where `Limit <= Start`, optionally sleeps for fixed reader latency, then returns a reader sized to `Limit - Start`. `dummyReader.Read` returns EOF when exhausted, otherwise chooses the smaller of buffer length and remaining bytes, sleeps according to byte count, advances `bytesRead`, and returns EOF together with the final bytes on the last read.

`dummyMultiRangeDownloader.Add` increments a wait group and launches a goroutine. The goroutine sleeps by `calculateLatency(length, perMBLatency)`, copies exactly `length` zero bytes into the output via `io.Copy` and `io.LimitReader`, and invokes the callback with offset, bytes written, and error. `Close` waits for all added work; `Wait` blocks; `Error` always returns nil; `GetHandle` returns a fixed dummy handle.

## State and Persistence Behavior
The wrapper itself stores only the wrapped bucket and latency settings. Dummy readers store read progress in memory. Multi-range downloader state is only a wait group. No data is persisted and no actual object bytes are read from the wrapped bucket. Writes and metadata mutations still persist wherever the wrapped bucket persists them.

## Dependencies and Integration Points
The file depends on `gcs.Bucket`, `gcs.StorageReader`, `gcs.MultiRangeDownloader`, `cloud.google.com/go/storage` read handles, `context`, `io`, `sync`, and `time`. It is intended to fit transparently anywhere a `gcs.Bucket` is consumed, with special behavior only for content reads.

## Risks and Edge Cases
The read path requires explicit ranges; callers expecting whole-object reads will receive an error. Range validation rejects zero-length ranges because `rangeLen <= 0`, while multi-range downloader accepts zero length. `time.Sleep` ignores context cancellation once a dummy read starts. `dummyMultiRangeDownloader` has no aggregate error state even if `io.Copy` fails, and concurrent writes to the same output are caller-dependent. Returning zero-filled data can hide bugs that depend on real content.

## Test Signals
`dummy_io_bucket_test.go` covers constructor nil behavior, delegated metadata/mutation methods, range validation, reader latency, per-MB latency computation, reader EOF behavior, read handles, multi-range zero data, concurrent add calls, close waiting, latency, fixed handles, and nil error status.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket_test.go

## Purpose
`dummy_io_bucket_test.go` validates the dummy IO bucket wrapper, dummy reader, and dummy multi-range downloader. It ensures non-read bucket methods delegate to the wrapped bucket and read paths synthesize zero bytes with the configured latency and handles.

## Important APIs, Types, and Functions
The tests exercise `NewDummyIOBucket`, `dummyIOBucket` methods, `NewReaderWithReadHandle`, `NewMultiRangeDownloader`, `calculateLatency`, `newDummyReader`, `dummyReader.Read/Close/ReadHandle`, and `dummyMultiRangeDownloader.Add/Close/Wait/Error/GetHandle`. They use `TestifyMockBucket`, `gcs` request types, testify assertions, `bytes.Buffer`, `sync.WaitGroup`, and timing checks.

## Control Flow
Constructor tests validate nil passthrough and non-nil wrapping. Delegation tests set expectations on the mock bucket for `Name`, `BucketType`, delete, stat, list, copy, folder operations, move, update, and `GCSName`. Reader tests request a valid byte range and assert a `dummyReader` with matching length; missing or invalid ranges should return errors. Latency tests measure elapsed time for fixed reader latency and per-MB read latency.

Reader-specific tests read full buffers, partial buffers, beyond EOF, close, and fetch read handles. Multi-range tests call `Add` with callbacks, wait for completion, verify output length and zero content, launch multiple concurrent adds, ensure `Close` waits for callback completion, validate latency bounds, check fixed handle value, and confirm `Error` returns nil.

## State and Persistence Behavior
The tests use in-memory buffers and mock state only. They observe mutable reader state (`bytesRead`) and multi-range wait-group completion. No durable storage is used.

## Dependencies and Integration Points
The test suite depends on the dummy bucket implementation, `gcs` interfaces, `TestifyMockBucket`, testify `assert`/`require`, and standard library concurrency and IO utilities. It is the direct regression suite for dummy IO behavior.

## Risks and Edge Cases
Timing assertions can be sensitive to scheduler variance, especially the upper bound in the multi-range latency test. The test suite verifies delegation for many methods but does not include all write methods such as chunk writers/finalize/flush/compose in the excerpted coverage. It also does not test context cancellation during latency sleeps or write errors from the output writer.

## Test Signals
Signals are strong for constructor behavior, zero-filled reader and downloader output, EOF semantics, fixed handles, wait behavior, and many pass-through methods. Gaps remain around context cancellation, output write failures, and aggregate multi-range error reporting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/dummy_io_bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/bucket.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/bucket.go

## Purpose
`fake/bucket.go` implements an in-memory `gcs.Bucket` for tests. It models object metadata, object contents, generation and metageneration checks, listing semantics, compose/copy/update/delete/move operations, HNS folder entries, appendable writes, readers, and multi-range downloaders without contacting GCS.

## Important APIs, Types, and Functions
`NewFakeBucket(clock, name, bucketType)` returns a `gcs.Bucket` backed by `bucket`. Internal types include `fakeObject`, sorted `fakeObjectSlice`, sorted `fakeFolderSlice`, and `bucket`. Helper methods perform name validation, prefix searching, object minting, folder minting, object copying, min-object conversion, precondition checking, and create/update insertion.

Public bucket methods include `Name`, `BucketType`, `ListObjects`, `NewReaderWithReadHandle`, `CreateObject`, `CreateObjectChunkWriter`, `CreateAppendableObjectWriter`, `FlushPendingWrites`, `FinalizeUpload`, `CopyObject`, `ComposeObjects`, `StatObject`, `UpdateObject`, `DeleteObject`, `MoveObject`, folder CRUD/rename, `NewMultiRangeDownloader`, and `GCSName`.

## Control Flow
Object creation validates names, reads request contents, validates CRC32C/MD5 and generation/metageneration preconditions, mints metadata with incremented generation, checksums, size, media link, storage class, and simulated clock update time, then inserts or replaces the sorted object entry. Appendable writer creation eventually calls `createOrUpdateFakeObject` with append mode, which reads existing object content and appends new bytes.

Listing computes a start name from prefix and continuation token, applies `StartOffset`, limits by prefix upper bound and max results, and emits either objects or collapsed runs depending on delimiter rules. It has extra HNS handling so folder entries representing prefixes are returned as prefixes rather than objects. Continuation tokens skip duplicate collapsed run results across pages.

Readers locate the object by name and optional generation, then slice content according to requested range and return a `FakeReader` with an opaque handle. Copy validates destination name, source existence/generation/metageneration, copies metadata/data, and assigns a fresh destination generation. Compose validates source count, reads each source, enforces component-count limits, creates the destination object, sets combined component count, and clears MD5 for composite behavior.

Stat panics for invalid extended-attribute requests that cannot be served from cache-like paths, returns not-found for missing objects, and optionally returns extended attributes. Update validates generation/metageneration then modifies object metadata and increments metageneration. Delete ignores missing objects and wrong generation, but enforces metageneration preconditions. Move validates source and destination, copies the record to the new name with new generation, removes the source, and re-sorts.

Folder operations maintain a separate sorted folder list plus prefix-object compatibility entries for HNS. `CreateFolder` creates both a folder record and a prefix object; `DeleteFolder` removes both if present; `RenameFolder` rewrites matching folder and object prefixes. `NewMultiRangeDownloader` validates object existence/generation and non-nil data before returning a fake downloader over that object.

## State and Persistence Behavior
All state is in memory under an invariant mutex: sorted object slice, sorted folder slice, and `prevGeneration`. Invariants ensure object names are strictly increasing and no object generation exceeds `prevGeneration`. Metadata maps are copied before returning to avoid exposing internal state. The fake uses the provided clock for object/folder creation and updates in most paths, though folder rename uses `time.Now()` directly.

## Dependencies and Integration Points
The fake bucket depends on `gcs` types and constants, `storageutil` conversions and object reads, `timeutil.Clock`, `syncutil.InvariantMutex`, checksum libraries, sorting, UTF-8 validation, path utilities, and standard IO. It is registered by `fake/bucket_test.go` against the common bucket test suite and is used by caching integration tests and other storage tests.

## Risks and Edge Cases
The fake intentionally approximates GCS and may diverge. It does not model multiple historical generations for one object, has mixed clock sources in `RenameFolder`, and `MoveObject` lacks explicit locking despite mutating shared slices. `CreateAppendableObjectWriter` calls `b.objects.find` without locking. HNS prefix/folder compatibility is subtle and easy to desynchronize. `DeleteObject` treats missing and wrong-generation deletes as success, which matches some idempotent test needs but may hide caller assumptions.

## Test Signals
The common fake bucket test registration in `bucket_test.go` exercises generic bucket behavior. Other files in this subset rely on this fake for cache integration and reader/downloader behavior. Specific risks around concurrent move/append locking and HNS folder semantics need targeted tests beyond the common suite.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/bucket.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/bucket_test.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/bucket_test.go

## Purpose
`fake/bucket_test.go` registers the in-memory fake bucket with the shared bucket behavior test suite. It provides a standard way to validate that `fake.NewFakeBucket` satisfies expected `gcs.Bucket` semantics.

## Important APIs, Types, and Functions
`TestBucket` runs ogletest suites. The package `init` function defines `makeDeps`, creates a fixed `timeutil.SimulatedClock`, constructs `NewFakeBucket(clock, "some_bucket", gcs.BucketType{})`, and calls `gcstesting.RegisterBucketTests(makeDeps)`.

## Control Flow
During test initialization, the common storage fake testing package receives a dependency factory. For each shared bucket test, the factory supplies a fresh simulated clock and fake bucket. `TestBucket` then runs all registered ogletest suites.

## State and Persistence Behavior
The only local state is per-test fake bucket state and simulated clock state. The fixed non-zero time makes metadata timestamps deterministic. No durable persistence is used.

## Dependencies and Integration Points
The file integrates `internal/storage/fake/testing` shared bucket tests, `gcs` bucket type definitions, ogletest, `timeutil`, and context. It is the main conformance link between fake bucket behavior and the wider storage test contract.

## Risks and Edge Cases
This file only registers the default non-HNS, non-zonal bucket type. HNS folder behavior, zonal append behavior, and multi-range downloader helpers require separate targeted tests. The strength of this test depends on breadth of the shared `gcstesting` suite, which is outside this file.

## Test Signals
The signal is broad generic bucket conformance for the fake bucket. It validates standard create/read/list/stat/update/delete-style behavior through shared tests, while leaving specialized fake-only behavior to other tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/bucket_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_multi_range_downloader.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/fake_multi_range_downloader.go

## Purpose
`fake_multi_range_downloader.go` provides a test implementation of `gcs.MultiRangeDownloader` backed by in-memory object data. It supports normal range reads, configurable sleep, default immediate errors, status errors, short reads, and read handles.

## Important APIs, Types, and Functions
`fakeMultiRangeDownloader` stores a fake object, wait group, error fields, sleep duration, short-read flag, and handle. Constructors include `NewFakeMultiRangeDownloader`, `NewFakeMultiRangeDownloaderWithHandle`, `NewFakeMultiRangeDownloaderWithShortRead`, `NewFakeMultiRangeDownloaderWithSleep`, `NewFakeMultiRangeDownloaderWithSleepAndDefaultError`, and `NewFakeMultiRangeDownloaderWithStatusError`. `createFakeObject` converts a `MinObject` plus bytes into the internal object representation.

The interface methods are `Add`, `Close`, `Wait`, `Error`, and `GetHandle`.

## Control Flow
`Add` first handles a configured default error by invoking the callback immediately with zero bytes. Otherwise it validates range inputs similarly to the Google storage reader: negative length errors, offsets beyond size error, offsets less than or equal to negative size map to the whole object, negative offsets count from the end, and positive ranges are truncated to remaining data. Invalid input stores an error and calls the callback immediately.

For valid input, `Add` starts a goroutine, optionally halves length for short-read simulation, sleeps, writes the selected object byte slice to the output, converts short or failed writes to an error, and invokes the callback. `Close` waits and returns the stored error. `Wait` blocks on all goroutines. `Error` returns the configured status error independently of transfer errors. `GetHandle` returns the configured handle.

## State and Persistence Behavior
State is in memory. The downloader holds a copy of object metadata/data and tracks asynchronous transfer completion with a wait group. It has mutable error fields but no locking around `err`, so concurrent failing `Add` calls can race in tests that run with the race detector.

## Dependencies and Integration Points
The file depends on `gcs.MultiRangeDownloader`, `storageutil.ConvertMinObjectToObject`, `io.Writer`, `sync.WaitGroup`, and `time`. It is returned by `fake.Bucket.NewMultiRangeDownloader` and can be directly constructed by tests needing controlled downloader behavior.

## Risks and Edge Cases
The error assignment after goroutine writes appears inverted: `if fmrd.err != nil { fmrd.err = err }` preserves nil rather than recording a new asynchronous write error. There is no mutex for `err`. Short-read mode can invoke callbacks with fewer bytes but nil error if the write itself succeeds, depending on caller expectations. `Error` reports `statusErr`, not transfer errors, so callers must know which method they are validating.

## Test Signals
This subset does not include direct tests for every constructor, but `fast_stat_bucket_test.go` uses `NewFakeMultiRangeDownloader`, and `dummy_io_bucket_test.go` covers a separate dummy downloader. Recommended tests would cover negative offsets, range truncation, default errors, status errors, short reads, handle propagation, and concurrent error recording.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_multi_range_downloader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_object_writer.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/fake_object_writer.go

## Purpose
`fake_object_writer.go` implements the fake bucket's `gcs.Writer`. It buffers uploaded bytes in memory, validates GCS-style preconditions, and creates or updates the fake bucket object when closed or flushed.

## Important APIs, Types, and Functions
`FakeObjectWriter` embeds an `io.WriteCloser`, owns a `bytes.Buffer`, `storage.ObjectAttrs`, a pointer to the fake bucket, the original `gcs.CreateObjectRequest`, the created `MinObject`, and an append-mode flag. Methods are `Write`, `Close`, `Flush`, `ObjectName`, and `Attrs`. `NewFakeObjectWriter` validates object name and initializes writer attrs from the request.

## Control Flow
`Write` checks preconditions against the current buffer contents, then appends bytes to the buffer. `Close` validates preconditions again, calls `createOrUpdateFakeObject` with buffered contents and append mode, and stores the resulting min object when successful. `Flush` delegates to `Close` and returns the current buffer length. `ObjectName` and `Attrs` expose writer metadata used by wrappers such as debug and caching buckets.

## State and Persistence Behavior
Before close, uploaded data lives only in the writer buffer. On close or flush, the writer mutates the fake bucket's in-memory object slice through `createOrUpdateFakeObject`. The writer keeps the last created `MinObject` in `Object`. No durable persistence exists.

## Dependencies and Integration Points
The writer depends on `cloud.google.com/go/storage.ObjectAttrs`, `gcs.CreateObjectRequest`, `storageutil.ConvertObjToMinObject`, and fake bucket helpers `checkName`, `preconditionChecks`, and `createOrUpdateFakeObject`. It is returned by `bucket.CreateObjectChunkWriter` and `bucket.CreateAppendableObjectWriter`, and consumed by fake bucket `FinalizeUpload`/`FlushPendingWrites`.

## Risks and Edge Cases
Precondition checks during `Write` use the buffer before adding the new bytes, so checksum preconditions over final content can fail late at `Close` rather than at the write that made them invalid. The writer itself has no synchronization; callers should not write concurrently. Repeated `Flush` or `Close` can recreate/update the object more than once because there is no closed flag. Append mode depends on reading existing bucket content during object update.

## Test Signals
Direct tests are not in this subset. Behavior is indirectly exercised by fake bucket shared tests, cache writer/finalize tests, and storage utilities that create objects through writers. Targeted tests should cover checksum failures, generation and metageneration preconditions, append mode, repeated close/flush, and object attrs exposure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_object_writer.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_reader.go -->
# sources/user-network-fs/gcsfuse/internal/storage/fake/fake_reader.go

## Purpose
`fake_reader.go` defines the fake storage reader returned by the fake bucket. It combines an `io.ReadCloser` with a storage read handle so tests can exercise handle-aware read paths.

## Important APIs, Types, and Functions
`FakeReader` embeds `io.ReadCloser` and stores `Handle []byte`. Its only method, `ReadHandle`, returns the stored handle as `storagev2.ReadHandle`.

## Control Flow
There is no complex control flow. The embedded reader handles `Read` and `Close`; callers use `ReadHandle` to retrieve the opaque handle. `fake.Bucket.NewReaderWithReadHandle` constructs it with an `io.NopCloser` over a byte reader and the handle `opaque-handle`.

## State and Persistence Behavior
The reader state is whatever the embedded `ReadCloser` maintains plus the immutable handle slice reference. It has no persistence and does not mutate bucket state.

## Dependencies and Integration Points
The file depends on `io` and `cloud.google.com/go/storage.ReadHandle`. It is used by `fake/bucket.go` and by tests such as `fast_stat_bucket_test.go` that need a simple successful `gcs.StorageReader`.

## Risks and Edge Cases
`ReadHandle` returns the underlying slice directly, so a caller can mutate the handle bytes. There is no nil protection around the embedded reader; constructing `FakeReader` with a nil `ReadCloser` would panic on reads through embedding. Otherwise the implementation is intentionally minimal.

## Test Signals
Direct tests are minimal or indirect. `fast_stat_bucket_test.go` verifies a `FakeReader` can be returned through a wrapper unchanged, and fake bucket tests exercise reading data through this type. A focused test could verify handle propagation and read/close delegation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/storage/fake/fake_reader.go -->
