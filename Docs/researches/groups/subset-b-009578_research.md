# Research Report: subset-b-009578

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go

## Purpose
This test file validates `CacheHandler`, the file-cache layer that turns GCS objects into local cache handles and coordinates file-info LRU entries, downloader jobs, local cache files, regex filtering, eviction cleanup, invalidation, sparse-mode setup, and cache destruction. It is the main integration-style test surface between `internal/cache/file`, `internal/cache/file/downloader`, `internal/cache/lru`, fake GCS storage, and cache filesystem utilities.

## Important fixtures and APIs
`cacheHandlerTestArgs` bundles the fake bucket, object metadata, LRU cache, `JobManager`, `CacheHandler`, local download path, and cache key. `initializeCacheHandlerTestArgs` creates fake storage, a test object, a volume-block-aware LRU cache, a `JobManager`, and a `CacheHandler` initialized with regex and sparse settings from `cfg.FileCacheConfig`. Helpers such as `createObject`, `addTestFileInfoEntryInCache`, `getDownloadJobForTestObject`, `isEntryInFileInfoCache`, and `doesFileExist` keep tests focused on externally visible cache behavior.

## Control flow and state behavior
The tests exercise the lifecycle from `GetCacheHandle` through file-info insertion, job creation, reads, eviction, and invalidation. Existing file-info entries are reused when generation and job state match; generation changes, failed jobs, invalid jobs, or missing jobs for incomplete files force cleanup and replacement. Eviction paths call `cleanUpEvictedFile`, which invalidates the download job, removes it from `JobManager`, truncates/removes the local file, and tolerates already-missing cache files. Regex tests show include filtering is applied before exclude precedence, and a file that matches both include and exclude is rejected. Range-read tests assert that non-random reads can create cache handles, while random range reads may bypass file caching unless full-object caching is requested.

## Dependencies and integration points
The file depends on fake storage and a mocked storage-control client, `data.FileInfo`, `downloader.JobManager`, `lru.Cache`, cache utility path creation and truncation, volume block size discovery, metrics/tracing no-op handles, and integration-test filesystem cleanup utilities. It implicitly documents the contract between `CacheHandler` and `CacheHandle.Read`: non-parallel sequential cache reads can synchronously wait for needed offsets, while parallel mode may return read errors when foreground reads do not wait the same way.

## Risks and edge cases
The most important risks covered are stale local state after GCS generation changes, deleted cache files with live LRU entries, eviction while downloads are in progress, concurrent `GetCacheHandle` and `InvalidateCache`, and size accounting that must use cache-volume block size. Some assertions use sleeps or timing-sensitive async job completion, which can be flaky if downloader cleanup timing changes. The destroy test has a likely copy/paste issue checking `job2` by asking for `minObject1` twice, so it may under-cover the second object job.

## Test signals
Coverage is broad: creation paths, generation replacement, failed/invalid job recovery, local-file deletion errors, eviction in parallel and non-parallel modes, regex include/exclude behavior, random-read bypasses, same-file and different-file concurrency, invalidation truncation of open file handles, full handler destroy, and block-size-sensitive LRU accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go

## Purpose
This file defines `JobManager`, the singleton mount-level coordinator for asynchronous object download jobs. Its role is deduplicating one `Job` per bucket/object path, configuring those jobs with cache paths, permissions, LRU file-info cache, concurrency limits, metrics, tracing, and file-cache settings, and removing jobs when they complete, fail, or are invalidated.

## Important APIs and types
`NewJobManager` constructs the manager and chooses a global weighted semaphore size from `FileCacheConfig.MaxParallelDownloads`, defaulting to effectively unlimited. `CreateJobIfNotExists` returns an existing job or creates a `Job` with a cache `FileSpec` derived from `util.GetDownloadPath`. `GetJob` returns a job by object and bucket name. `InvalidateAndRemoveJob` invalidates a job if present. `DownloadChunkSizeMb` exposes configured chunk size for sparse setup. `Destroy` invalidates all tracked jobs.

## Control flow and state behavior
The manager maintains a `map[string]*Job` keyed by `util.GetObjectPath(bucket, object)`. All map access is guarded by a `locker.Locker`. Job creation registers a callback that calls back into `removeJob`, letting the job remove itself from the manager after terminal cleanup. `InvalidateAndRemoveJob` intentionally releases the manager lock before calling `Job.Invalidate`; this avoids deadlock because invalidation eventually invokes the remove callback, which needs the same manager lock.

## Dependencies and integration points
The manager is configured by `cfg.FileCacheConfig`, cache data/file utilities, the shared `lru.Cache`, `gcs.Bucket` and `gcs.MinObject`, metrics and tracing handles, and `golang.org/x/sync/semaphore`. It is normally owned by `CacheHandler`, which inserts file-info entries before creating jobs and relies on manager invalidation during eviction.

## Risks and edge cases
The remove callback captures the object and bucket names from job creation; if object metadata is mutated by tests or callers after creation, the callback still uses the captured pointer fields and could remove the wrong key if mutable `MinObject.Name` were changed. The global semaphore is shared across jobs but first per-file parallel worker behavior is implemented inside `Job`, so manager-level limits depend on job code honoring the shared semaphore. `Destroy` snapshots jobs before invalidating, avoiding map iteration mutation hazards.

## Test signals
`downloader_test.go` verifies create/get/invalidate/destroy behavior, default permissions, repeated create reuse, concurrent `GetJob`, concurrent invalidation, and concurrent create versus invalidate. `jm_parallel_downloads_test.go` verifies manager-wide parallel download limits across jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go

## Purpose
This ogletest suite validates `JobManager` behavior and provides shared setup for many downloader tests. It creates fake GCS storage, seeded objects, cache directories, LRU file-info entries, default `Job` instances, and cleanup logic used by job, parallel, and sparse downloader suites.

## Important fixtures and APIs
`downloaderTest` holds `defaultFileCacheConfig`, a current `Job`, fake `gcs.Bucket`, current object metadata, LRU cache, fake storage, `FileSpec`, and `JobManager`. `setupHelper` enables invariant checks, resets the cache directory, creates fake storage with a mocked storage-layout call, initializes a default job test object, and constructs a `JobManager`. `waitForCrcCheckToBeCompleted` polls terminal job status because subscriber notification can occur before final CRC validation.

## Control flow and state behavior
The tests cover `JobManager.CreateJobIfNotExists`, `GetJob`, `InvalidateAndRemoveJob`, and `Destroy`. They assert that create deduplicates by bucket/object path, populates download paths and permissions, and stores jobs under manager lock. Invalidation tests start downloads, call manager invalidation, and expect the job status to become `Invalid` and the manager map entry to disappear. Destroy snapshots and invalidates multiple jobs in different states.

## Dependencies and integration points
The suite uses fake storage (`storage.NewFakeStorageWithMockClient`), `storageutil.CreateObjects`, cache data types, `lru.Cache`, cache utility path helpers, no-op metrics/tracing, and integration cleanup operations. It is coupled to the `Job` test helper in `job_test.go` via `initJobTest`, so the manager tests also depend on file-info cache setup.

## Risks and edge cases
Concurrency tests check that manager locking prevents duplicate reads and deletion races but do not assert exact callback counts for manager removal. The global `cacheDir` under `$HOME/cache/dir` is shared across tests, so parallel test execution outside the suite's expectations could conflict. `TearDown` invalidates both the current job and manager, which is correct but can mask bugs where callbacks are already removed.

## Test signals
The file verifies non-existing and existing create/get paths, default file/dir permissions, concurrent `GetJob`, invalidating absent and present jobs, concurrent invalidation, destroying multiple jobs, and concurrent create/invalidate calls. It is a primary signal for the `JobManager` locking and callback-removal contract.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/downloader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go

## Purpose
This testify test file verifies `JobManager` and `Job` parallel-download behavior under realistic fake-storage conditions. It focuses on object-size boundaries, O_DIRECT toggling, per-file parallelism, manager-wide `MaxParallelDownloads`, and simultaneous downloads of multiple objects.

## Important fixtures and APIs
Helper functions create random objects in fake buckets, configure fake storage, configure temporary LRU/cache directories, and initialize file-info cache entries. `TestParallelDownloads` is table-driven over object size, chunk size, per-file worker count, global max parallel downloads, subscribed offset, and O_DIRECT. `TestMultipleConcurrentDownloads` starts two jobs from one manager and waits for both subscribers.

## Control flow and state behavior
The setup inserts `data.FileInfo` for each object before creating jobs, matching the production expectation that downloader status updates mutate an existing LRU entry. Jobs are created through `JobManager.CreateJobIfNotExists`, subscribers are registered, and `Download(..., waitForDownload=false)` starts background downloads. Tests then wait on subscriber channels to observe enough downloaded bytes and inspect cache file content up to the notified offset.

## Dependencies and integration points
The tests use fake GCS storage and mocked storage layout, `lru.Cache`, `data.FileInfo`, no-op metrics/tracing, `cfg.FileCacheConfig`, and `util.GetDownloadPath`. They integrate manager-level semaphore configuration (`MaxParallelDownloads`) with `parallelDownloadObjectToFile` internals. O_DIRECT behavior is exercised by configuration, though actual fallback depends on platform file-opening semantics.

## Risks and edge cases
The tests use one-second timeouts and background goroutines, so slow environments can produce false failures. They verify content up to notified offsets, not necessarily full final completion or semaphore counts. The first per-file goroutine does not consume a global semaphore token by design; these tests exercise that indirectly but do not count actual concurrent readers.

## Test signals
Signals include downloading entire objects when object size exceeds worker-count times chunk size, capping ranges at object size, operating with O_DIRECT disabled, and allowing two concurrent object downloads under a manager-wide limit while both produce readable cached content.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/jm_parallel_downloads_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go

## Purpose
This file implements the core downloader `Job`, an asynchronous state machine that downloads one GCS object into one local cache file, updates file-info cache progress, notifies subscribers waiting for offsets, validates CRC, handles cancellation/invalidation, and chooses sequential or parallel download mode.

## Important APIs and types
`JobStatus` stores `Name`, `Err`, and contiguous downloaded `Offset`. Status names are `NotStarted`, `Downloading`, `Completed`, `Failed`, and `Invalid`. `NewJob` configures object, bucket, LRU cache, read size, cache file spec, removal callback, file-cache config, semaphore, metrics/tracing, and volume block size. Public APIs are `Download`, `GetStatus`, `Invalidate`, `IsParallelDownloadsEnabled`, and `IsExperimentalParallelDownloadsDefaultOn`.

## Control flow and state behavior
`Download` validates the requested offset, starts one background `downloadObjectAsync` from `NotStarted`, returns immediately or subscribes for offset progress, and surfaces terminal `Failed`/`Invalid`/`Completed` states. Subscribers are notified when status is failed, invalid, or has reached their offset. Sequential downloading opens ranged GCS readers with `NewReaderWithReadHandle`, copies in `ReadChunkSize` segments, propagates read handles between sequential ranges, and calls `updateStatusOffset` after each segment. `downloadObjectAsync` creates the cache file, delegates to sequential or parallel download, truncates final file size, validates CRC, marks completion, and always runs cleanup. Cleanup cancels context, invokes the manager callback once, clears context fields, and closes `doneCh`.

## State and persistence behavior
The local file is created/truncated before download. Progress is persisted in the shared `lru.Cache` by replacing the `data.FileInfo` value without changing LRU order; update failure due to missing entry is interpreted as invalidation during eviction. CRC mismatch erases file-info cache and truncates/removes the local file. `Invalidate` cancels an active download, blocks until the goroutine exits, marks the status invalid, removes the manager callback, and notifies subscribers.

## Dependencies and integration points
The job depends on `gcs.Bucket.NewReaderWithReadHandle`, cache `data.FileInfo`, `lru.Cache`, cache utilities for file creation and CRC, `locker`, logger, metrics/tracing, and semaphores shared by `JobManager`. Parallel and sparse behavior are implemented in companion files but share this struct's fields and locks.

## Risks and edge cases
The locking is subtle: `cancel` releases `job.mu` while waiting to avoid deadlock with the download goroutine. Subscriber notification can report `Downloading` with enough offset before final CRC validation, so callers must handle later terminal failure. `validateCRC` dereferences `job.object.CRC32C`; it relies on populated object metadata when CRC is enabled. O_DIRECT fallback handles invalid file-open errors, but platform-specific direct I/O behavior remains risky.

## Test signals
`job_test.go` covers state initialization, subscriber notification, offset updates, sequential download, `Download` state branches, cancellation, invalidation races, CRC cleanup, config helpers, and cache-file creation. `job_testify_test.go` verifies read-handle propagation with mocked GCS readers.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go

## Purpose
This legacy ogletest file is the main behavioral suite for `Job`. It validates state-machine transitions, subscriber mechanics, file-info cache mutation, sequential async download, public `Download`, cancellation, invalidation, CRC behavior, and cache file creation.

## Important fixtures and APIs
`initJobTest` creates a fake GCS object, builds a cache `FileSpec`, creates an LRU cache, constructs a `Job`, and inserts the required `data.FileInfo` entry. Helpers verify invalid errors, cache-file content, file-info entries, and cache path layout. The file notes that new tests should be added to the newer testify suite.

## Control flow and state behavior
Early tests validate `init`, `subscribe`, `notifySubscribers`, and `updateStatusAndNotifySubscribers`. Offset update tests confirm that updating an existing file-info entry changes both LRU value and job status, while missing entries return `lru.ErrEntryNotExist` and size mismatch returns `lru.ErrInvalidUpdateEntrySize`. Download tests cover starting from `NotStarted`, joining an existing `Downloading` job, observing `Completed`, surfacing async failure, returning existing failed/invalid states, rejecting offsets larger than object size, and allowing caller context cancellation without necessarily cancelling the background job.

## State and persistence behavior
The tests assert local file bytes are written with expected permissions and file-info offsets advance. Cleanup tests verify context cancellation, callback execution, context field clearing, and `doneCh` closure. CRC tests prove mismatched checksum deletes the local file and erases LRU state when CRC is enabled, while disabled CRC leaves tampered data and cache metadata intact.

## Dependencies and integration points
The suite uses fake storage, `storageutil`, random byte generation, `data.FileInfo`, `lru.Cache`, cache utilities, no-op metrics/tracing, and a weighted semaphore. It is tied to production locking because invariant checks are enabled and many tests run concurrent `Download` and `Invalidate` operations.

## Risks and edge cases
Several tests rely on timing, polling, or async cleanup ordering. A disabled CRC cancellation test is documented as flaky. Tests intentionally mutate object size to simulate failures, which is useful but not a production-realistic mutation path. Concurrent tests check outcomes but do not run under the Go race detector by default.

## Test signals
The file provides strong regression signals for status names, subscriber removal, callback exactly-once behavior, invalidation during active download, concurrent download/invalidate calls, CRC mismatch cleanup, context-canceled error classification, and O_DIRECT/non-O_DIRECT cache file creation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go

## Purpose
This testify suite adds mock-based downloader tests, primarily to verify exact GCS reader requests and read-handle propagation that are hard to assert with the fake storage suite. It is the migration target for new `Job` tests.

## Important fixtures and APIs
`JobTestifyTest` embeds `suite.Suite` and owns a context, default file-cache config, `Job`, object metadata, LRU cache, file spec, and `storage.TestifyMockBucket`. `initReadCacheTestifyTest` constructs a `Job` around the mock bucket, creates a file-info cache entry, and uses disk block size for job construction.

## Control flow and state behavior
`Test_downloadObjectToFile_WithReadHandle` creates a 10 MiB object, configures sequential read size to 5 MiB, and sets mocked `NewReaderWithReadHandle` expectations for two ranges. The first range uses a nil read handle; the fake reader returns an opaque handle; the second range must pass that handle back. The test subscribes to the full object offset, invokes `downloadObjectToFile`, and validates subscriber notification, file content, and file-info cache progress.

## Dependencies and integration points
This file depends on testify suite/assert/mock, `storage.TestifyMockBucket`, fake readers, cache data/LRU utilities, diskutil, metrics/tracing no-ops, and `semaphore.NewWeighted`. It complements fake-storage tests by asserting request structs, not just final file content.

## Risks and edge cases
The mock returns the same fake reader object for both ranges; because the reader wraps a string reader, this works for the test expectation but could hide independent-reader lifecycle details. The file path under `$HOME/cache/dir` is shared with other downloader tests. Only the sequential read-handle path is covered here; error propagation and cancellation remain in legacy tests.

## Test signals
The main signal is that sequential downloads reuse GCS read handles across range requests, request exact byte ranges, notify offset subscribers, write complete local content, and update file-info cache to at least object size.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/job_testify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go

## Purpose
This file implements the parallel download mode for `Job`. It splits an object into configured byte ranges, fans those ranges out to worker goroutines, writes them into the cache file at fixed offsets, tracks contiguous downloaded ranges, updates file-info progress as the prefix becomes complete, and respects job cancellation plus manager-wide parallelism limits.

## Important APIs and functions
`downloadRange` opens a ranged GCS reader, copies bytes into a provided writer, captures metrics, optionally uses memory-aligned buffers for O_DIRECT, and returns the reader's read handle. `updateRangeMap` merges newly downloaded intervals and updates job status when a range starting at zero grows. `downloadOffsets` is the worker loop over `job.rangeChan`. `parallelDownloadObjectToFile` creates workers, feeds ranges, opportunistically starts additional workers when semaphore slots open, and delegates final error handling to `handleJobCompletion`.

## Control flow and state behavior
`parallelDownloadObjectToFile` sizes ranges by `DownloadChunkSizeMb`, starts up to `ParallelDownloadsPerFile` workers while reserving global semaphore tokens for workers after index zero, and publishes every object range to `rangeChan`. Each worker preserves its own GCS read handle across assigned ranges. In experimental default mode, progress is tracked inside `downloadRange` at `ReadChunkSize` granularity; otherwise `downloadOffsets` updates range completion after each full range. `updateRangeMap` stores bidirectional endpoints so left and right adjacent ranges can be merged cheaply.

## Dependencies and integration points
The file relies on `errgroup`, `gcs.ReadObjectRequest`, `data.ObjectRange`, cache utility aligned-copy support, logger, metrics, and the `Job` lock and file-info update mechanism from `job.go`. It uses `job.maxParallelismSem`, shared by all manager jobs, as the cross-file concurrency limiter.

## Risks and edge cases
Range-map correctness is critical because subscribers only know about contiguous data from offset zero. The first worker deliberately does not release/acquire the global semaphore, which ensures progress but means global max is not a hard cap on total goroutines. Closing `rangeChan` in `handleJobCompletion` assumes no sender continues after a context path returns. O_DIRECT errors can surface as non-context errors, so code joins `ctx.Err()` when cancellation is detected.

## Test signals
Parallel tests cover ranged content writing, full parallel object download, cancellation, range-map merge cases, read-handle propagation under concurrency, O_DIRECT disabled mode, object-size capping, and concurrent downloads across jobs.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go

## Purpose
This ogletest suite validates the parallel-download-specific behavior of `Job` while reusing the broader downloader test fixture. It exists to run analogous downloader scenarios with `EnableParallelDownloads=true` and to directly test range-map merging.

## Important fixtures and APIs
`parallelDownloaderTest` embeds `downloaderTest` and configures `FileCacheConfig` with parallel downloads enabled, `ParallelDownloadsPerFile=3`, `DownloadChunkSizeMb=3`, CRC enabled, and a 4 MiB write buffer. Tests call `downloadRange`, `parallelDownloadObjectToFile`, and `updateRangeMap` directly.

## Control flow and state behavior
`Test_downloadRange` downloads non-overlapping end, beginning, middle, and zero-byte ranges and checks file content at offsets. `Test_parallelDownloadObjectToFile` subscribes to an offset, downloads a 10 MiB object through the parallel path, verifies notification, local content, and file-info cache. Cancellation is tested by cancelling `job.cancelCtx` before invoking the parallel path. Range-map tests cover no existing ranges, extension at the end, extension at the start, filling a gap to merge two ranges, and inserting an isolated range.

## Dependencies and integration points
The tests rely on fake GCS storage, cache utilities, random byte generation, `data.FileSpec`, and production `updateStatusOffset` behavior. They interact with `rangeMap` directly to validate the internal representation used by subscriber progress notification.

## Risks and edge cases
The fake storage note in `job_test.go` about ranged reads is partly avoided here by parallel-specific paths, but fake storage behavior remains a dependency. Zero-byte range behavior is accepted as nil error, which may be important if future code rejects empty ranges. The tests check state after successful returns but do not assert exact goroutine count or semaphore acquisition.

## Test signals
Signals include correct offset writes for arbitrary ranges, full object reconstruction, subscriber offset notification, context-canceled error propagation, and bidirectional endpoint map invariants for merging contiguous downloaded ranges.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go

## Purpose
This testify suite verifies parallel download read-handle behavior with mocked GCS readers. It complements content-based parallel tests by asserting how `NewReaderWithReadHandle` is called across chunks and workers.

## Important fixtures and APIs
`ParallelDownloaderJobTestifyTest` embeds `JobTestifyTest` and configures parallel downloads with three workers, 3 MiB chunks, CRC enabled, and 4 MiB write buffer. The main test creates four expected ranges for a 10 MiB object and assigns fake readers with a shared opaque handle.

## Control flow and state behavior
The test sets mock expectations for four ranged `NewReaderWithReadHandle` calls. The first chunk must use a nil read handle, middle chunks may use nil or propagated handles because worker scheduling is nondeterministic, and the fourth chunk is expected to use a non-nil handle. Counters protected by a mutex record total call count and nil-handle calls, allowing nondeterministic worker ordering while still bounding expected behavior. After download, the test verifies subscriber notification, local file content, and file-info cache.

## Dependencies and integration points
The suite uses `storage.TestifyMockBucket`, fake readers, testify mock matchers, cache utilities, and the shared helper functions from `test_util.go`. It directly validates the contract between parallel workers and the GCS read-handle optimization.

## Risks and edge cases
Because parallel scheduling is nondeterministic, the test intentionally allows a range of nil-handle counts. The expectation that the last chunk has a non-nil read handle can be sensitive to worker assignment. The mock content is partitioned by chunk and assumes exact chunk ranges, so changes to range sizing or chunk scheduling require coordinated test updates.

## Test signals
The file signals that parallel downloads issue one GCS reader per chunk, propagate handles within workers, notify subscribers, reconstruct the full file, and update the file-info cache despite concurrent reader calls.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/parallel_downloads_job_testify_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go

## Purpose
This file implements sparse/chunked read support for `Job`. Instead of downloading a full object prefix, it checks whether requested byte ranges are already cached, downloads missing configured chunks, tracks in-flight chunks to avoid duplicate work, updates sparse `FileInfo.DownloadedChunks`, and returns whether the cache can satisfy the read.

## Important APIs and functions
`HandleSparseRead` is the public sparse path. It retrieves `FileInfo`, checks `DownloadedChunks.ContainsRange`, computes missing chunks through `getChunksToDownload`, downloads missing chunks in an `errgroup`, waits for already-in-flight chunks, and verifies the requested range. `downloadSparseRange` downloads a byte range, writes it to the cache file using `io.NewOffsetWriter`, updates `DownloadedChunks`, and calls `lru.Cache.UpdateSize` with only newly added bytes.

## Control flow and state behavior
Missing chunks are computed from `ByteRangeMap.GetMissingChunks`. `job.inflightChunks` maps chunk IDs to close-on-completion channels and is protected by `job.mu`. New chunks are marked in-flight before goroutines start; duplicate callers receive wait channels instead of launching duplicate downloads. After all download attempts finish, the initiator closes and deletes its chunk channels. Sparse file-info entries use `Offset` as a max-uint sentinel elsewhere, while actual cached data is represented by `DownloadedChunks`.

## Dependencies and integration points
The sparse path depends on `data.ByteRangeMap`, `data.FileInfo`, LRU lookup/update-size APIs, `gcs.Bucket.NewReaderWithReadHandle`, random-read metrics, `errgroup`, the shared global semaphore, logger, and the cache file created by higher-level cache-handler code. It integrates with `CacheHandler` sparse initialization, which allocates the byte-range map and sets sentinel offsets.

## Risks and edge cases
`HandleSparseRead` downloads full missing chunks, not just the requested byte range, so object-size capping in `downloadSparseRange` is important. If a download fails, cleanup still closes in-flight channels, so waiters can continue and then verify cache state. `downloadSparseRange` opens an existing file with `O_WRONLY`; missing local files surface as errors. `UpdateSize` intentionally can push LRU current size past max until a later insert, so sparse growth eviction is deferred.

## Test signals
Sparse tests cover chunk-boundary calculation, invalid ranges, in-flight chunk deduplication, direct sparse range download and byte-range tracking, cache-hit fast path, and downloading missing chunks before verifying requested reads.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go

## Purpose
This ogletest suite validates sparse downloader behavior around chunk selection, duplicate in-flight work, sparse range downloads, and `HandleSparseRead` cache-hit outcomes.

## Important fixtures and APIs
`sparseDownloaderTest` embeds `downloaderTest` and configures experimental chunk cache, 20 MiB sparse chunks, CRC enabled, and experimental parallel default. Tests manually create sparse `data.FileInfo` values with `data.NewByteRangeMap` and max-uint offsets to mirror `CacheHandler` sparse initialization.

## Control flow and state behavior
`Test_getChunksToDownload` covers aligned and unaligned ranges, end capping, and invalid offset ranges. `Test_getChunksToDownload_WithInflight` pre-populates `job.inflightChunks` and asserts that already-running chunks produce wait channels while other chunks are newly marked in-flight. `Test_DownloadRange` creates the local file and sparse file-info entry, downloads `[10 MiB, 30 MiB)`, checks file bytes, and verifies `DownloadedChunks.ContainsRange`.

## Dependencies and integration points
The tests rely on fake storage, cache utility file creation, `data.ByteRangeMap`, LRU insertion and lookup without changing order, and random byte generation. They validate sparse code but also exercise `lru.UpdateSize` indirectly during `downloadSparseRange`.

## Risks and edge cases
The test named `HandleSparseRead_NeedsDownload` expects a request `[15 MiB, 25 MiB)` to download chunks covering `[0, 40 MiB)`, proving chunk expansion rather than exact-range download. The suite does not cover download failure cleanup, waiter context cancellation, or concurrent callers racing through `HandleSparseRead`; those remain risk areas for in-flight channel handling.

## Test signals
Signals include chunk ID calculation for unaligned reads, invalid range rejection, in-flight chunk deduplication, sparse file writes at offsets, byte-range map mutation, pre-downloaded cache hits, and post-download cache-hit verification with content validation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/sparse_downloads_job_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go

## Purpose
This file contains shared helper functions for downloader testify and parallel tests. It reduces duplication around retrieving fake object metadata, validating local cache file contents, and validating file-info cache entries.

## Important APIs
`getMinObject` stats an object from a test bucket with `ForceFetchFromGcs` and returns a value. `verifyFileTillOffset` checks file existence, permissions, and content prefix up to a requested offset. `verifyCompleteFile` checks permissions, size, and full content. `verifyFileInfoEntry` retrieves cache metadata and asserts generation, downloaded offset, and content size. `getFileInfo` builds a `data.FileInfoKey` and looks it up in the LRU cache.

## Control flow and state behavior
The helpers are assertion wrappers rather than production logic. They encode important expectations: cache files use the configured `FileSpec.FilePerm`; parallel downloads may leave file size larger than object content until final truncation, so complete validation accepts file size greater than or equal to content length; and file-info offsets are allowed to be greater than or equal to the expected offset.

## Dependencies and integration points
The file depends on `testing`, `testify/assert`, `os`, `reflect`, `data.FileSpec`, `lru.Cache`, fake/mock storage bucket types, and GCS object metadata. It is used by testify suites and manager parallel tests to validate downloader side effects consistently.

## Risks and edge cases
`getMinObject` panics on stat errors, which is acceptable for test setup but hides test helper failure as panic rather than assertion. Content comparison reads the whole file into memory, which is fine for current test sizes but would be expensive for very large fixtures. The prefix validators rely on the caller passing an offset no larger than the expected content length.

## Test signals
Although it has no tests of its own, this file centralizes the signal that downloader tests care about three persistent side effects: local cache file permissions/content, file-info cache generation/offset/content-size, and object metadata retrieval from fake storage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/downloader/test_util.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go

## Purpose
This file defines `SharedChunkCacheManager`, a chunk-addressing helper for a cache that can be shared across gcsfuse mount instances. It computes stable chunk paths based on bucket, object name, generation, and chunk index, provides temp paths for atomic chunk writes, and applies include/exclude regex filtering.

## Important APIs and types
`NewSharedChunkCacheManager` stores cache directory, chunk size, permissions, config, and compiled regexes. `ShouldExcludeFromCache` applies include-then-exclude logic to `bucket/object` paths. `GenerateTmpPath` appends a random 16-hex-character temp suffix to a final chunk path. `GetChunkIndex`, `GetChunkSize`, `GetObjectDir`, `GetChunkPath`, `GetFilePerm`, and `GetDirPerm` expose path, sizing, and permissions. `computeObjectHash` SHA256-hashes length-prefixed bucket/object/generation fields.

## Control flow and state behavior
The manager itself does not persist data; it deterministically maps object identity to filesystem paths. Object directories are sharded by the first four hex digits of the SHA256 hash as `<cache>/<p1>/<p2>/<hash>`. Chunk files are named `<start>_<end>.bin` using configured fixed chunk size. Temp path generation uses `math/rand/v2.Uint64`, producing collision-resistant names but not cryptographic randomness.

## Dependencies and integration points
The manager depends on `cfg.FileCacheConfig`, regex compilation, `filepath`, SHA256/hex, file permissions, logging for invalid regex warnings, and GCS bucket/object metadata. It is designed for shared-cache code that can use mkdir/rename-style atomic operations, though those operations are not implemented in this file.

## Risks and edge cases
If `SharedCacheChunkSizeMb` is zero, chunk size becomes zero; tests document this current behavior, but callers must avoid division by zero in `GetChunkIndex`. Invalid regexes only warn and become nil filters, potentially caching more objects than intended. The hash uses generation, so overwrites naturally map to a new directory but require external cleanup for old generations.

## Test signals
`shared_chunk_cache_manager_test.go` verifies constructor fields, regex precedence, chunk index and size calculations, exact hash-derived paths, temp-path format and uniqueness over repeated calls, and permission getters.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go

## Purpose
This testify test file validates `SharedChunkCacheManager` path generation, regex filtering, chunk sizing, temp-name generation, and permission accessors.

## Important fixtures and APIs
Tests construct managers with temporary directories and targeted `cfg.FileCacheConfig` values. Fake buckets and minimal objects are used for `ShouldExcludeFromCache`. Table-driven tests cover include/exclude combinations, offsets, chunk sizes, object directory hashes, chunk file paths, and temp path expectations.

## Control flow and state behavior
Constructor tests assert the manager stores cache directory and computes `chunkSize` from `SharedCacheChunkSizeMb`. Regex tests confirm no-filter caching, include-only rejection of non-matches, exclude-only rejection of matches, and exclude precedence when both regexes match. Path tests hard-code expected SHA256 shard paths, acting as compatibility tests for the hash input format. Temp path tests check `<chunk>.16hex.tmp` format and generate 100 paths for one chunk to detect collisions.

## Dependencies and integration points
The suite depends on `t.TempDir`, `filepath`, testify assert/require, `cfg.FileCacheConfig`, fake GCS buckets, and `timeutil.RealClock`. It is tightly coupled to `computeObjectHash` output, which is useful for compatibility but makes intended hash-format changes require test updates.

## Risks and edge cases
The "default chunk size" test expects zero when config is zero, which documents a potentially dangerous default if callers later divide by chunk size. Temp collision testing with 100 random values is probabilistic and cannot prove uniqueness. Regex invalid-input behavior is not tested, despite constructor warning-and-ignore logic.

## Test signals
Signals include stable shared-cache directory layout, deterministic chunk file naming by byte offsets, include/exclude cache policy, random temp suffix format, practical temp uniqueness, and preservation of configured file and directory permissions.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/shared_chunk_cache_manager_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go

## Purpose
This file implements a generic size-bounded LRU cache keyed by strings and storing values that implement `ValueType.Size() uint64`. It is used by file-cache metadata and stat cache code to bound memory or disk-accounting state and to drive eviction callbacks at higher layers.

## Important APIs and types
`Cache` stores `maxSize`, `currentSize`, a most-recent-first linked list, and a key-to-element index guarded by `locker.RWLocker`. Public APIs are `NewCache`, `Insert`, `Erase`, `LookUp`, `LookUpWithoutChangingOrder`, `UpdateWithoutChangingOrder`, `UpdateSize`, and `EraseEntriesWithGivenPrefix`. Error sentinels include invalid entry, oversized entry, invalid update size, and missing entry.

## Control flow and state behavior
`Insert` rejects nil or oversized values, updates existing entries while moving them to the front, adds new entries at the front, then evicts from the tail until `currentSize <= maxSize`, returning evicted values to the caller. `LookUp` moves entries to front; `LookUpWithoutChangingOrder` uses a read lock and preserves recency. `UpdateWithoutChangingOrder` replaces a value only if the key exists and size is unchanged. `EraseEntriesWithGivenPrefix` snapshots matching keys under read lock, then deletes them under write lock.

## State and persistence behavior
The cache is in-memory only. Its evicted values are returned so callers can perform external cleanup, such as invalidating download jobs and removing cache files. `UpdateSize` increments `currentSize` without changing the stored value or evicting immediately; this is intentionally used by sparse files whose downloaded byte count grows incrementally, but it can temporarily violate the invariant until future inserts trigger eviction.

## Dependencies and integration points
The cache depends on `container/list`, reflection-based invariant checks, strings prefix matching, and gcsfuse's locker package. File cache uses it for `data.FileInfo`; metadata stat cache uses it for stat entries; sparse downloader uses `UpdateSize`.

## Risks and edge cases
`NewCache` does not validate `maxSize`; invariant checks catch zero only when enabled. `UpdateSize` can make `currentSize > maxSize`, despite the invariant comment, so invariant checking during sparse size updates may be risky if enabled around that path. Prefix erasure is O(number of entries) and can be costly for large caches, hence benchmarks.

## Test signals
`lru_test.go` covers insert, overwrite, eviction ordering, multiple eviction, erase, prefix erase, update-without-order, lookup-without-order, and concurrent operations. Benchmarks cover insert, lookup, erase, mixed concurrency, million-entry insertion, and million-entry prefix deletion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go

## Purpose
This file defines performance benchmarks for the generic LRU cache. It measures common operations, concurrent mixed workloads, and large-scale prefix deletion scenarios relevant to file and metadata cache invalidation.

## Important benchmarks
`BenchmarkInsert` measures repeated insertions with unique keys. `BenchmarkLookUp` prepopulates 10,000 entries and measures repeated hits. `BenchmarkErase` measures erase cost while excluding setup insertion from the timer. `BenchmarkConcurrency` uses `RunParallel` with 30 percent inserts, 60 percent lookups, and 10 percent erases over a random key space. `BenchmarkInsert1Million` and `BenchmarkEraseEntriesWithGivenPrefix_1Million` exercise very large maps/lists.

## Control flow and state behavior
The benchmarks use the `testData` `ValueType` from `lru_test.go`. Large benchmarks recreate the cache inside each iteration with timers stopped, then measure the specific operation under test. Prefix deletion benchmark inserts one million entries with half under `prefix/` and times `EraseEntriesWithGivenPrefix("prefix/")`.

## Dependencies and integration points
The file depends on Go `testing`, `fmt`, `math/rand`, `time`, and the production `lru` package. The benchmark for prefix erase directly reflects metadata and file-cache invalidation workloads where many keys share a path prefix.

## Risks and edge cases
`BenchmarkConcurrency` seeds each goroutine's random source with `time.Now().UnixNano`, so repeated workers can occasionally share seeds if started very close together, though this is acceptable for benchmark variability. The million-entry benchmarks are memory-heavy and may be unsuitable for constrained CI by default. Benchmarks do not report allocations explicitly beyond standard Go benchmark output.

## Test signals
These are performance signals rather than correctness tests. They indicate whether changes to locking, list/index maintenance, or prefix scan logic materially affect common and large-scale cache operations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go

## Purpose
This ogletest suite validates correctness and concurrency behavior of the generic LRU cache. It verifies cache capacity enforcement, recency ordering, update semantics, prefix erasure, and thread safety under mixed operations.

## Important fixtures and APIs
`CacheTest` creates a `lru.Cache` with `MaxSize=50` and enables invariant checks. `testData` implements `ValueType` with a configurable `DataSize`. `insertAndAssert` centralizes insertion, expected evicted values, and expected error checks.

## Control flow and state behavior
Tests cover empty lookup, nil insert rejection, unknown lookup, filling to capacity, least-recently-used eviction after lookup changes recency, overwriting existing entries, multiple eviction for a large insert, rejecting values larger than max size, erasing present and absent keys, and prefix erasure. Update tests verify `UpdateWithoutChangingOrder` succeeds for same-size values, fails for missing keys or size changes, and does not move an entry to the front. Lookup-without-order tests prove read-only lookup also preserves eviction order.

## Dependencies and integration points
The suite imports `locker.EnableInvariantsCheck`, which makes internal list/index/current-size invariants active around lock operations. It uses Go `sync` and `math/rand` for concurrent tests. Prefix erasure tests reflect stat-cache and file-cache invalidation use cases.

## Risks and edge cases
`TestRaceCondition` is explicitly useful under `go test -race`; without race detector it mainly checks that operations complete. Concurrent prefix erasure only verifies no panic/race-like failure, not exact postcondition counts. Tests predate `UpdateSize`, so the sparse-size accounting API lacks direct unit coverage here.

## Test signals
The file gives strong correctness signals for LRU ordering, eviction return values, size validation, order-preserving update/lookup APIs used by downloader progress, prefix deletion, and coarse concurrent safety.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/lru/lru_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go -->
# sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go

## Purpose
This file implements the metadata `StatCache` interface on top of the shared LRU cache. It caches positive object entries, implicit directories, folder resources, and negative entries with expirations, while supporting bucket-name namespacing for dynamic mounts and prefix invalidation.

## Important APIs and types
`StatCache` exposes `Insert`, `InsertImplicitDir`, `AddNegativeEntry`, `Erase`, `LookUp`, `InsertFolder`, `LookUpFolder`, `AddNegativeEntryForFolder`, and `EraseEntriesWithGivenPrefix`. `NewStatCacheBucketView` wraps a shared `lru.Cache` with an optional bucket prefix. Internal `entry` stores either a `*gcs.MinObject`, `*gcs.Folder`, expiration, and an `implicitDir` flag.

## Control flow and state behavior
Object insertion avoids replacing a newer positive entry with older generation or metageneration data, but always replaces negative entries and equivalent-generation entries for freshness. Implicit directory insertion skips if an explicit object entry already exists, preventing inferred placeholders from overwriting real metadata. Negative entries store nil object/folder pointers. Lookup reads from LRU, expires stale entries by erasing them, returns nil metadata for negative hits, and synthesizes a minimal `MinObject` for implicit directory hits.

## State and persistence behavior
The cache is in-memory, expiration-driven, and LRU-bounded through `entry.Size`. Size estimation uses unsafe struct size, nested object/folder size helpers, a fixed positive-object overhead, and a heap-to-RSS conversion factor. Bucket views namespace keys by concatenating bucket name, bucket creation time from `FileInfoKey` analogs is not used here, and object path joining deliberately avoids `path.Join` to preserve trailing slash distinctions.

## Dependencies and integration points
The implementation depends on `lru.Cache`, GCS metadata types, logger, util size-estimation helpers, math/time, and prefix erasure from LRU. It is used by filesystem metadata paths that need to cache object existence, listings, folders, and managed-folder-like resources.

## Risks and edge cases
`AddNegativeEntryForFolder` stores an entry with `f:nil`, indistinguishable in shape from object negative entries except by key namespace chosen by caller. `InsertFolder` does not apply generation/metageneration replacement checks like object insert does. Prefix erasure delegates to raw string prefix matching and must be called with a prefix that respects bucket-view key construction and trailing slash semantics.

## Test signals
No tests are in this work item, but expected signals would include stale-generation rejection, negative-to-positive replacement, implicit directory non-overwrite, expiration erase-on-lookup, bucket namespace isolation, folder entry lookup, and prefix invalidation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/metadata/stat_cache.go -->
