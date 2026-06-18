# subset-b-009577 Research

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader_test.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader_test.go

## Purpose
This suite is the behavioral specification for the buffered read path around `BufferedReader`. It exercises construction, prefetch block reservation, queue invariants, fresh-start scheduling, foreground reads, background prefetch failures, fallback to another reader, and block lifetime under concurrent reads. The tests use deterministic fake readers that emit an A-Z byte pattern keyed by absolute offset, which makes block alignment and multi-block slicing observable.

## Important APIs, Types, And Functions
The suite type `BufferedReaderTest` owns common fixtures: a `gcs.MinObject`, mocked bucket, global block semaphore, `BufferedReadConfig`, static worker pool, noop metrics, and `gcsx.ReadTypeClassifier`. Helpers include `createFakeReaderWithOffset`, `assertBlockContent`, `assertReadResponseContent`, and `assertBufferContent`.

The tests directly exercise both public and package-private reader behavior: `NewBufferedReader`, `Destroy`, `CheckInvariants`, `scheduleNextBlock`, `scheduleBlockWithIndex`, `freshStart`, `prefetch`, and `ReadAt`. They also inspect internal fields such as `nextBlockIndexToPrefetch`, `randomSeekCount`, `numPrefetchBlocks`, `blockQueue`, `blockPool`, and callback-driven block `RefCount`.

## Control Flow And State
Construction tests verify the reader stores dependencies, creates a block queue and pool, initializes cancellable context state, reserves only the minimum useful number of blocks based on object size and `MinBlocksPerHandle`, and fails when the global semaphore cannot provide any block. Invariant tests intentionally corrupt queue length, random seek count, and prefetch block size to assert panics.

Scheduling tests show the reader calculates byte offsets from block indexes, submits urgent and non-urgent download tasks to the worker pool, sets absolute block offsets, advances `nextBlockIndexToPrefetch`, and leaves downloaded blocks in FIFO order. `freshStart` aligns arbitrary offsets down to a block boundary, schedules one urgent block plus initial prefetch blocks, caps by `MaxPrefetchBlockCnt`, stops at object end, and doubles `numPrefetchBlocks` for later sequential prefetch. `prefetch` respects queue capacity and available pool blocks; if the pool is exhausted, it does not advance scheduling state.

`ReadAt` tests cover EOF and empty-buffer returns, backward and forward seeks, queue discard/cancel behavior, multi-block reads, reads exactly to EOF, partial last-block reads, and the way sequential reads consume queued blocks and trigger more prefetch. Random reads increment `randomSeekCount`; after the threshold, the reader returns `gcsx.FallbackToAnotherReader` until the read classifier becomes sequential again, at which point the reader can reset and resume.

## State And Persistence Behavior
The state under test is in memory: prefetch queue contents, block-pool reservations, block readiness, cancellable download contexts, random-read counters, and callback-held reference counts. No persistent files are written by this test. The important lifetime rule is that returned `ReadResponse.Callback` releases block references; `Destroy` waits for callbacks before completing, and evicted in-use blocks are released only after the callback runs.

## Dependencies And Integration Points
The suite integrates `internal/block` prefetch blocks, `internal/gcsx` read requests/responses and read classification, `internal/storage` testify mocks, `internal/storage/fake` readers, `internal/workerpool`, `metrics.NewNoopMetrics`, `golang.org/x/sync/semaphore`, and `testify` assertions/suites. Mocked `Bucket.NewReaderWithReadHandle` calls validate GCS byte-range requests by `Range.Start` and sometimes `Range.Limit`.

## Risks And Edge Cases
The tests highlight risks around leaked semaphore permits, queue entries canceled while still in use, prefetch failures affecting unrelated foreground reads, mmap/block allocation failure, data races under concurrent reads, duplicate downloads for the same block, and stale fallback state after random access patterns. They also show that failed background prefetch is tolerated for the current read but becomes visible when the failed block is later read.

## Test Signals
Coverage is broad and high-signal for queue scheduling, fallback, concurrency, and resource release. The tests are mostly unit-level with mocked GCS and a real worker pool; they do not validate live Cloud Storage behavior or production timing, but they explicitly wait for block readiness to reduce races.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/buffered_reader_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/download_task.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedread/download_task.go

## Purpose
`download_task.go` defines the worker-pool task that downloads one GCS object byte range into one prefetch block for buffered reads. It bridges `BufferedReader` scheduling with GCS range readers and block readiness notifications.

## Important APIs, Types, And Functions
`downloadTask` embeds `workerpool.Task` and stores the target `gcs.MinObject`, `gcs.Bucket`, metrics handle, destination `block.PrefetchBlock`, cancellation context, and optional zonal-bucket read handle. Its single method, `Execute`, implements the workerpool task contract.

## Control Flow And State
`Execute` derives the block id from `block.AbsStartOff()/block.Cap()`, logs start time, and defers completion handling. It computes the GCS range as `[AbsStartOff, min(AbsStartOff+block.Cap(), object.Size))`, calls `bucket.NewReaderWithReadHandle`, and passes object name, generation, byte range, gzip read behavior from `object.HasContentEncodingGzip()`, and any read handle. It then copies exactly `end-start` bytes into the block with `io.CopyN`.

The deferred completion path notifies the block as `BlockStateDownloaded` on success or `BlockStateDownloadFailed` with the error on failure. It distinguishes client cancellation for trace logging, converts `gcs.NotFoundError` from reader creation into `gcsfuse_errors.FileClobberedError`, wraps other reader/copy errors with phase context, closes the reader, and always records downloaded byte count through `GcsDownloadBytesCount`.

## State And Persistence Behavior
The task mutates only the destination prefetch block and metrics. Persistence is external: bytes are streamed from GCS into an in-memory or mmap-backed block supplied by the block package. The task does not retry, cache to disk, or own block release.

## Dependencies And Integration Points
The file depends on `internal/block` for destination block status, `internal/storage/gcs` for range reads and object metadata, `internal/fs/gcsfuse_errors` for clobber detection, `internal/workerpool` for task execution, `metrics` for read-byte accounting, and `logger` for trace/error messages. It is scheduled by the buffered reader and consumed by block awaiters.

## Risks And Edge Cases
The code assumes the block capacity and absolute offset define a valid object range. `io.CopyN` treats short reads as errors, so partial content or premature EOF marks the block failed. Metrics count bytes copied before failure, which is useful but can surprise callers expecting only successful bytes. A nil `metricHandle` or nil block would panic; callers are responsible for construction.

## Test Signals
`download_task_test.go` covers success, generic reader creation errors, deadline/cancel behavior, cancellation while reading, and NotFound-to-FileClobbered conversion. It validates block status notifications and range requests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/download_task.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/download_task_test.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedread/download_task_test.go

## Purpose
This suite verifies `downloadTask.Execute` as the unit boundary between GCS range reads and prefetch block readiness. It ensures correct request construction, copied byte counts, failure propagation, cancellation classification, and clobbered-file error mapping.

## Important APIs, Types, And Functions
`DownloadTaskTestSuite` sets up a `gcs.MinObject`, `storage.TestifyMockBucket`, `block.GenBlockPool[block.PrefetchBlock]`, and noop metrics. Helpers include `getReadCloser` and `ctxCancelledReader`, a reader that returns `context.Canceled` during `Read`.

The tests instantiate `downloadTask` directly and call `Execute`, then inspect the destination block with `Size`, `Cap`, and `AwaitReady`.

## Control Flow And State
The success test expects `NewReaderWithReadHandle` to receive a `ReadObjectRequest` with object name, generation, and `[0,testBlockSize)` range, then verifies that copied content makes the block size equal to the test content and that block status becomes `BlockStateDownloaded`.

Failure tests cover reader creation returning a generic error, context deadline exceeded from the server, context canceled during reader creation after client cancellation, context canceled while copying from the reader, and `gcs.NotFoundError`. All failures notify `BlockStateDownloadFailed`; the NotFound case must wrap as `gcsfuse_errors.FileClobberedError`.

## State And Persistence Behavior
The suite uses an in-memory block pool and mocked/fake readers. There is no disk persistence. The observable state is block content, block status, and mocked bucket call count.

## Dependencies And Integration Points
The tests rely on the block prefetch pool, storage testify mock, fake reader wrapper, `gcs.ReadObjectRequest`, `workerpool.Task` embedding, `metrics.NewNoopMetrics`, `testify/suite`, and `semaphore.NewWeighted` for block pool construction.

## Risks And Edge Cases
The tests pin down cancellation as a failed block rather than a silent success. They also demonstrate that deadline exceeded is treated as ordinary failure, while client-side canceled contexts are still propagated as errors. They do not assert metrics values or reader close behavior.

## Test Signals
The suite gives strong signal for request range construction and block notification semantics. It is focused unit coverage and intentionally avoids running through `BufferedReader`.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedread/download_task_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler.go

## Purpose
This file implements the high-level buffered write handler used by file writes before data is uploaded to GCS. It accepts sequential writes, packs bytes into reusable blocks, hands full or flushed blocks to `UploadHandler`, tracks file size and mtime, supports grow-only truncation by zero filling, and finalizes or syncs uploads.

## Important APIs, Types, And Functions
`BufferedWriteHandler` exposes `Write`, `Sync`, `Flush`, `SetMtime`, `Truncate`, `WriteFileInfo`, `Destroy`, and `Unlink`. `bufferedWriteHandlerImpl` stores the current block, block pool, upload handler, `totalSize`, `mtime`, and `truncatedSize`. `WriteFileInfo` reports the visible size and mtime. `CreateBWHandlerRequest` carries the object, bucket, block limits, retry/timeout values, global semaphore, and trace handle. `NewBWHandler` constructs the block pool and upload handler.

## Control Flow And State
`Write` first checks `UploadError`, then enforces sequential offsets except for a pending truncate offset before data has caught up. If writing exactly at `truncatedSize`, it calls `writeDataForTruncatedSize` to append zero bytes through the normal buffering path. `appendBuffer` lazily obtains a block, copies as much data as fits, uploads full blocks immediately, and updates `totalSize`. Once `totalSize` reaches `truncatedSize`, the truncate marker is reset to `-1`.

`Sync` uploads a non-empty current block, waits for all queued block uploads, and for rapid-write buckets calls `FlushPendingWrites` to make bytes visible without finalization. It verifies returned size against `totalSize`, clears free block memory without destroying the active reservation, and returns any asynchronous upload error.

`Flush` checks prior upload errors, zero-fills any pending grow-truncate, uploads the current block, calls `Finalize`, validates final object size, then clears the block pool more aggressively. `Destroy` destroys pending upload state and clears blocks. `Unlink` cancels uploads and releases free blocks while intentionally keeping the last block reservation until file-handle close.

## State And Persistence Behavior
Write state is in-memory until the upload handler writes to GCS. `totalSize` may include bytes already uploaded and bytes still buffered. `truncatedSize` is deferred state: no data is written at `Truncate` time, but later `Write` or `Flush` materializes zero bytes. `mtime` is metadata cached for inode attribute responses and is not uploaded here.

## Dependencies And Integration Points
The handler depends on `internal/block` for pooled buffers, `internal/storage/gcs` for bucket/object abstractions, `UploadHandler` for streaming writes, `semaphore.Weighted` for global block limits, `logger` for resource cleanup failures, and `tracing` for upload trace propagation via the upload handler. It assumes the inode lock serializes write operations, so it does not protect its fields with mutexes.

## Risks And Edge Cases
The largest correctness risks are out-of-order writes, stale truncate offsets, async upload failures surfacing on later calls, block-pool leaks, and rapid-write size mismatches. Zero filling is chunked in 1 MiB pieces to avoid allocating the full truncated gap. A nil or misconfigured bucket/trace/block semaphore would fail outside this file's checks.

## Test Signals
`buffered_write_handler_test.go` covers offset enforcement, block splitting, sync/flush behavior for regional and rapid-write buckets, grow-truncate zero filling, size mismatches, upload-error propagation, destroy/unlink release behavior, and reflushing after upload failure.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler_test.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler_test.go

## Purpose
This suite specifies the buffered write handler's externally visible behavior: sequential writes, inode-visible file info, upload failure handling, sync versus flush semantics, grow-truncate behavior, and cleanup on destroy/unlink.

## Important APIs, Types, And Functions
`BufferedWriteTest` creates a fake bucket, global semaphore, and `BufferedWriteHandler` via `NewBWHandler`. It uses `fake.NewFakeBucket`, `storageutil.ReadObject`, generated random data, and mocked buckets/writers for size-mismatch paths. The suite frequently casts to `*bufferedWriteHandlerImpl` to inspect `current`, `totalSize`, `truncatedSize`, `uploadHandler.uploadCh`, and block pool free counts.

## Control Flow And State
Basic write tests show empty and non-empty writes update `WriteFileInfo`, block-size and multi-block writes advance `totalSize`, and writes with offsets less or greater than expected return `ErrOutOfOrderWrite` without changing size. Upload errors stored in `uploadHandler.uploadError` cause later `Write`, `Sync`, and `Flush` to fail.

Flush tests verify current-block upload, empty object creation, asynchronous error propagation, returned-object size validation across non-zonal, zonal, and Pirlo rapid-write variants, and repeated flush failure after an upload error. Sync tests verify full and partial blocks are uploaded, rapid-write buckets return a visible object after `FlushPendingWrites`, non-rapid buckets do not expose an unfinalized object, and size mismatch is rejected.

Truncate tests cover writing at the truncate offset, writing after truncating beyond current size, rejecting truncation below current size, zero-filling on flush, `WriteFileInfo` returning the max of total and truncate sizes, and rejecting stale writes at an old truncate position after later writes pass it.

Cleanup tests verify `Destroy` drains queued blocks and `Unlink` cancels active upload context and frees upload buffers while preserving one semaphore reservation for the last block.

## State And Persistence Behavior
The suite observes in-memory handler state and fake-bucket object contents. For rapid writes, `Sync` persists visible data to the fake bucket and returns object metadata. For non-rapid buckets, sync uploads chunks but does not finalize the object, so backdoor reads fail with `gcs.NotFoundError`.

## Dependencies And Integration Points
The tests integrate fake and mocked storage buckets, mocked writers, `gcs.BucketType` including zonal and Pirlo rapid-write states, tracing noop handles, global block semaphores, and integration-test random data helpers.

## Risks And Edge Cases
Important covered risks include size mismatch after GCS finalization/flush, upload errors that occur between writes, accidental backwards writes after grow-truncate, and semaphore leaks on unlink. The tests do not directly assert trace spans or logger output.

## Test Signals
The suite gives strong unit and fake-storage coverage for handler-level semantics. It complements `upload_handler_test.go`, which tests the lower async uploader directly.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/buffered_write_handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler.go

## Purpose
`upload_handler.go` implements the asynchronous streaming uploader behind buffered writes. It owns the GCS writer, a bounded channel of full blocks, one uploader goroutine, error state, cancellation, finalization, rapid-write flushing, and block return to the pool.

## Important APIs, Types, And Functions
`UploadHandler` stores `uploadCh`, `wg`, block pool, `gcs.Writer`, atomic upload error, cancel function, `sync.Once` for uploader startup, bucket/object settings, chunk retry/timeout settings, block size, and trace handle. `CreateUploadHandlerRequest` carries construction dependencies. Key methods are `newUploadHandler`, `Upload`, `createObjectWriter`, `UploadError`, `uploader`, `uploadBlock`, `Finalize`, `ensureWriter`, `FlushPendingWrites`, `CancelUpload`, `AwaitBlocksUpload`, and `Destroy`.

## Control Flow And State
`Upload` increments the wait group, ensures a writer exists, starts `uploader` exactly once, and enqueues the block. `createObjectWriter` builds a `gcs.CreateObjectRequest`, creates a background context with propagated trace and cancel function, and chooses `CreateAppendableObjectWriter` for rapid-write append to an unfinalized object; otherwise it uses `CreateObjectChunkWriter`.

The uploader goroutine reads blocks from `uploadCh`, calls `uploadBlock`, releases each block to the pool, and marks the wait group done. `uploadBlock` ignores nil blocks, short-circuits if an upload error already exists, seeks the block to offset zero, copies to the GCS writer, suppresses `context.Canceled` as local unlink behavior, and stores converted GCS errors atomically.

`Finalize` waits for queued blocks, closes the upload channel, ensures a writer even for empty-file flows, and calls `bucket.FinalizeUpload`. `FlushPendingWrites` waits, ensures a writer, and calls `bucket.FlushPendingWrites` without closing the channel. `Destroy` drains queued blocks, marks wait-group work done, releases blocks, and closes the channel.

## State And Persistence Behavior
Data persists to GCS through the writer. Blocks are reused after upload regardless of success, so upload failure is represented separately in `uploadError`. The GCS writer and cancel function are initialized lazily and then retained. Finalize closes the channel; flush keeps the stream open for more writes.

## Dependencies And Integration Points
This file depends on `internal/block`, `internal/storage/gcs`, `logger`, `tracing`, `sync`, and `atomic.Pointer[error]`. It is created and driven by `buffered_write_handler.go` and delegates all object-writing semantics to the bucket interface.

## Risks And Edge Cases
Because `Upload` calls `wg.Add(1)` before `ensureWriter`, a writer-creation error path can leave wait-group accounting inconsistent if callers later wait on the same handler. Channel close order is also sensitive: `Finalize` closes `uploadCh`, so later `Upload` calls would panic. Error pointers store addresses of local error variables, which escape safely in Go but require care when changing code. Context cancellation is intentionally suppressed only for copy errors, not writer creation/finalize/flush errors.

## Test Signals
`upload_handler_test.go` covers writer selection, request parameters, multiple block upload and release, copy errors, finalize/flush error storage, cancel behavior, await behavior, and destroy drain behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler_test.go -->
# sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler_test.go

## Purpose
This suite verifies `UploadHandler` as the async block-to-GCS writer. It focuses on writer selection, upload queue processing, block release, error persistence, finalize/flush behavior, cancellation, request metadata, and channel destruction.

## Important APIs, Types, And Functions
`UploadHandlerTest` constructs a mocked bucket, block pool, and upload handler. Helper `createUploadHandlerWithObjectOfGivenSize` configures append scenarios. Helpers `assertUploadFailureError`, `assertAllBlocksProcessed`, and `createBlocks` observe async completion and block pool state. Standalone tests cover `UploadError`.

## Control Flow And State
Writer creation tests assert appendable writer selection for zonal and Pirlo rapid-write unfinalized objects, and chunk writer selection for non-rapid, finalized, or local-inode flows. Ensure-writer tests cover successful and failed lazy writer creation.

Upload tests enqueue multiple blocks, finalize, and verify all blocks return to the free pool in reusable form. Copy-error tests force writer `Write` failures and assert `UploadError` is stored while all blocks are still processed and released. `AwaitBlocksUpload` waits for all queued blocks without finalizing.

Finalize and flush tests cover both existing-writer and lazy-writer paths, writer creation failures, bucket finalize/flush failures, returned object propagation, and error storage. Request-parameter tests validate generation/metageneration preconditions, content encoding/type, and chunk transfer timeout for existing GCS objects and local-inode writes.

Destroy tests place blocks directly in `uploadCh`, both open and preclosed, and assert `Destroy` releases blocks, drains wait-group accounting, empties the channel, and leaves it closed.

## State And Persistence Behavior
The suite uses mock writers rather than real persistence. State assertions focus on `uh.writer`, `uploadError`, `uploadCh`, `wg`, and block pool free counts. Cancellation is observed by replacing `cancelFunc` with a closure.

## Dependencies And Integration Points
Tests use mocked storage bucket and writer types, `internal/block`, `gcs.Object`/`MinObject`, `gcs.BucketType`, tracing noop, testify mock/suite, and semaphores.

## Risks And Edge Cases
The tests expose sensitive async behavior around wait groups and channel closure. They also show that once an upload error occurs, subsequent blocks are skipped but still released. One gap is direct coverage for `context.Canceled` suppression inside `uploadBlock`.

## Test Signals
The suite provides strong unit coverage for upload-handler internals. It complements handler-level fake-storage tests that validate actual object visibility and size checks.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/bufferedwrites/upload_handler_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map.go

## Purpose
`ByteRangeMap` tracks downloaded chunks for sparse file cache mode. It records chunk presence rather than exact byte ranges, allowing cache reads to determine whether requested ranges are fully backed locally and how many bytes should count toward cache occupancy.

## Important APIs, Types, And Functions
`DefaultChunkSize` is 1 MiB. `ByteRangeMap` stores a mutex, chunk size, total file size, a `map[uint64]bool` of downloaded chunk ids, and `totalBytes`. Public methods are `NewByteRangeMap`, `AddRange`, `ContainsRange`, `GetMissingChunks`, `TotalBytes`, `Clear`, and `Chunks`. Private helpers are `chunkID` and `chunkSizeOf`.

## Control Flow And State
`NewByteRangeMap` normalizes a zero chunk size to the default. `AddRange` locks for writing, treats empty or inverted ranges as no-op, maps `[start,end)` to inclusive chunk ids, marks any previously absent chunks, and increments `totalBytes` by each new chunk's physical size. `chunkSizeOf` accounts for the final partial chunk and returns zero for chunks starting beyond file size.

`ContainsRange` and `GetMissingChunks` use read locks and the same chunk-id conversion. Empty ranges are considered contained and have no missing chunks. `Chunks` returns a sorted list of downloaded ids for debugging and tests.

## State And Persistence Behavior
All state is in memory and protected by `sync.RWMutex`. The map is coarse-grained: adding a partial byte range marks the whole containing chunk downloaded. `totalBytes` is a sum of chunk sizes, not requested byte counts.

## Dependencies And Integration Points
The file depends only on the standard library `slices` and `sync`. It is embedded in `data.FileInfo` for sparse cache mode and initialized by `CacheHandler` with the downloader chunk size.

## Risks And Edge Cases
Callers must ensure actual downloads align with the chunk size; otherwise `ContainsRange` may claim local coverage for bytes not really downloaded. Ranges beyond file size can mark out-of-bounds chunk ids but add zero bytes for fully beyond-end chunks. The design is intentionally chunk-level and not suitable for exact sub-chunk coverage.

## Test Signals
`byte_range_map_test.go` covers partial chunks, overlaps, gaps, empty ranges, total byte accounting including partial final chunks, clearing, sorted chunk lists, chunk-size helper behavior, and basic concurrent access.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map_test.go

## Purpose
This file tests chunk-level sparse range tracking in `ByteRangeMap`. It documents the core behavior that any partial range marks full chunks, cache coverage is all-or-nothing per chunk, and total bytes are accounted by chunk sizes.

## Important APIs, Types, And Functions
Tests cover `AddRange`, `ContainsRange`, `GetMissingChunks`, `TotalBytes`, `Clear`, `Chunks`, and the private `chunkSizeOf`. The test constant `MB` mirrors the default 1 MiB chunk size.

## Control Flow And State
`TestByteRangeMap_AddRange` is table driven and verifies empty maps, partial chunks, non-overlapping additions, repeated additions, spanning ranges, gap filling, overlap, and invalid ranges. Contains/missing tests build a sparse set of chunks 0, 2, and 5 and query covered, missing, and gapped ranges.

Total-byte tests verify idempotent additions, gap filling, and partial last-chunk accounting. Clear resets map and bytes. `TestByteRangeMap_ConcurrentAccess` runs one writer and one reader goroutine to exercise the locking contract. Chunk alignment tests assert partial range additions mark the entire chunk as present while adjacent chunks remain missing.

## State And Persistence Behavior
The suite uses only in-memory maps. State assertions observe downloaded chunk ids and `totalBytes`.

## Dependencies And Integration Points
The file uses `testing` and `testify/assert`. It does not involve file cache jobs or disk I/O, but it establishes behavior relied on by sparse cache file metadata.

## Risks And Edge Cases
The tests make the coarse chunk contract explicit: a 100-byte range marks a 1 MiB chunk. They do not cover very large chunk ids, ranges beyond file size in `AddRange`, or race-detector assertions beyond "run with -race" suitability.

## Test Signals
The suite is focused and high signal for `ByteRangeMap` semantics. It should catch accidental changes from chunk-granular to byte-granular accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/byte_range_map_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/file_info.go

## Purpose
This file defines file-cache metadata used by the LRU and cache handlers. It provides stable cache keys, cache value sizing, sparse-mode downloaded-byte accounting, and local file path/permission specs.

## Important APIs, Types, And Functions
`InvalidKeyAttributes` is the error message for missing key fields. `FileInfoKey` stores bucket name, bucket creation time, and object name; `Key` delegates to `GetFileInfoKeyName`. `GetFileInfoKeyName` concatenates bucket name, bucket creation Unix time, and object name using preallocated byte storage.

`FileInfo` stores key, object generation, offset, file size, sparse-mode flag, optional `DownloadedChunks`, and cache-directory volume block size. Methods `ContentSize` and `Size` support logical content accounting and LRU `ValueType` size accounting. `FileSpec` carries local cache path and permissions. `NewFileInfo` centralizes field initialization.

## Control Flow And State
Key generation fails if bucket or object name is empty. For non-sparse files, `ContentSize` returns `FileSize`. For sparse files with a `DownloadedChunks` map, it returns downloaded chunk bytes instead of full object size. `Size` passes `ContentSize` to `diskutil.GetSpeculativeFileSizeOnDisk`, rounding by cache volume block size.

## State And Persistence Behavior
`FileInfo` is an in-memory cache value and describes persistent local cache files, but it does not perform I/O. `Offset` has two meanings: downloaded prefix length for non-sparse mode and `MaxUint64` sentinel in sparse mode as initialized by `CacheHandler`.

## Dependencies And Integration Points
The file depends on `diskutil` for physical-size estimation and on `ByteRangeMap` for sparse downloads. `CacheHandler`, `CacheHandle`, downloader jobs, and the LRU cache use these types to validate generations, offsets, cache size, and local file paths.

## Risks And Edge Cases
The key format is simple concatenation without separators, so it relies on bucket creation time and names being sufficient to avoid practical ambiguity. `FileInfoKey.Key` does not pass `BucketCreationTime` in some callers that construct only bucket/object names, making the Unix value zero in those contexts. Sparse `ContentSize` returns full file size if `DownloadedChunks` is nil, which is a fallback that can overstate sparse occupancy.

## Test Signals
`file_info_test.go` validates key generation errors and size rounding. `file_info_benchmark_test.go` tracks the optimized key-generation path.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info_benchmark_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/file_info_benchmark_test.go

## Purpose
This benchmark measures the optimized `GetFileInfoKeyName` implementation used to generate file-cache keys. It exists to guard allocation/performance-sensitive key construction in the cache path.

## Important APIs, Types, And Functions
`BenchmarkGetFileInfoKeyName_Optimized` creates a `time.Time` from `TestTimeInEpoch`, resets the benchmark timer, and repeatedly calls `GetFileInfoKeyName(TestObjectName, bucketCreationTime, TestBucketName)` inside `b.Loop()`.

## Control Flow And State
The benchmark has no setup beyond the timestamp conversion. It discards key and error results, focusing only on function cost. It uses constants from `file_info_test.go`.

## State And Persistence Behavior
No persistent state is touched. The benchmark observes CPU/allocation behavior of in-memory string construction.

## Dependencies And Integration Points
It depends on Go's `testing` benchmark API and `time`. It is tied to `file_info.go` and reuses test constants from the same package.

## Risks And Edge Cases
The benchmark measures only the valid-key path and does not benchmark empty bucket/object errors or unusually long names. Its utility depends on running with Go versions that support `b.Loop()`.

## Test Signals
This is a performance signal rather than correctness coverage. It complements unit tests for key behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info_benchmark_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/file_info_test.go

## Purpose
This file tests file-cache metadata key construction and size accounting. It documents the expected string key format and the distinction between logical content size and rounded physical cache size.

## Important APIs, Types, And Functions
Constants define a test bucket, object, generation, epoch time, file size, and expected key. `getTestFileInfoKey` builds a reusable `FileInfoKey`. Tests cover `FileInfoKey.Key`, invalid key fields, `NewFileInfo`, `ContentSize`, and `Size`.

## Control Flow And State
The key test verifies concatenation of bucket name, Unix creation time, and object name. Empty bucket or object name returns `InvalidKeyAttributes` and an empty key. `ContentSize` returns the file content size for a non-sparse `FileInfo`. `Size` rounds a 23-byte file up to a 4096-byte block size.

## State And Persistence Behavior
The suite is entirely in memory. It creates `FileInfo` values but no cache files.

## Dependencies And Integration Points
It uses `testing`, `time`, `fmt`, and `testify/assert`. It indirectly validates the `diskutil` integration via `FileInfo.Size`.

## Risks And Edge Cases
Sparse-mode `ContentSize`, nil `DownloadedChunks`, zero or one block size, and cache-key collision concerns are not covered here. Those behaviors are covered only indirectly elsewhere.

## Test Signals
The tests provide basic correctness checks for stable key naming and LRU size accounting.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/file_info_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/object_range.go -->
# sources/user-network-fs/gcsfuse/internal/cache/data/object_range.go

## Purpose
`ObjectRange` is a small data-transfer type representing a byte range within a GCS object. It is intended for cache/download coordination where start and end offsets need to travel together.

## Important APIs, Types, And Functions
The file defines one exported struct:

```go
type ObjectRange struct {
    Start int64
    End   int64
}
```

There are no methods, validation helpers, or constants.

## Control Flow And State
There is no control flow. The struct stores two signed offsets and leaves range semantics to callers.

## State And Persistence Behavior
The type is in-memory metadata only. It does not persist data or interact with files.

## Dependencies And Integration Points
It has no imports. Its package location makes it available to cache data, file, and downloader code that need object-range metadata.

## Risks And Edge Cases
Because the type does not define whether `End` is inclusive or exclusive and does not validate ordering or non-negativity, callers must document and enforce those invariants at use sites.

## Test Signals
No direct tests are listed for this file. Coverage is likely through consumers if any.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/data/object_range.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle.go

## Purpose
`cache_handle.go` implements per-open-object reads from the local file cache. A `CacheHandle` decides whether a read can be served from the local file, whether to wait for or trigger a downloader job, when to fall back to GCS, and how to update LRU recency and sequential/random read state.

## Important APIs, Types, And Functions
`CacheHandle` stores the local `*os.File`, optional `downloader.Job`, file-info LRU cache, `cacheFileForRangeRead`, and atomic sequential-read state (`isSequential`, `prevOffset`). Public methods are `NewCacheHandle`, `Read`, `IsSequential`, and `Close`. Important private helpers are `validateCacheHandle`, `shouldReadFromCache`, `getFileInfoData`, and `validateEntryInFileInfoCache`.

## Control Flow And State
`Read` validates the handle, rejects offsets outside object size, loads `FileInfo` without changing LRU order, and has a rapid/unfinalized-object guard that falls back when the requested offset is beyond the cached size. It determines whether the access remains sequential before updating `prevOffset`. Random reads do not wait for downloads; if range caching is disabled, they also avoid starting a job unless enough data is already cached.

The method clamps `requiredOffset` to object size. Sparse-mode reads delegate to `fileDownloadJob.HandleSparseRead` and require a cache hit; otherwise they fall back. Non-sparse reads with a job inspect job status, maybe call `Download(requiredOffset, waitForDownload)`, and then use `shouldReadFromCache` to ensure the job is valid and sufficiently advanced. If the job is nil, the file-info cache must show the whole file is present.

After readiness is established, `Read` calls `fileHandle.ReadAt`. EOF or unexpected EOF is accepted only when the number of bytes read equals the clamped requested length. Finally it validates the cache entry again with `changeCacheOrder=true` so the LRU marks the file recently used.

`IsSequential` returns false if the handle has already switched to random mode, if the current offset moves backward, or if the gap from previous offset exceeds `downloader.ReadChunkSize`. `Close` closes and nils the local file handle.

## State And Persistence Behavior
Persistent bytes live in a local cache file managed by downloader jobs and read through `ReadAt`. Metadata lives in the LRU `FileInfo` cache. The handle itself persists per-open state: sequential/random classification and last offset. Atomic fields allow concurrent reads to inspect/update read state, but broader file/cache coordination relies on downloader and cache concurrency guarantees.

## Dependencies And Integration Points
The file integrates `internal/cache/data`, `internal/cache/file/downloader`, `internal/cache/lru`, `internal/cache/util`, `logger`, and `internal/storage/gcs`. It is created by `CacheHandler.GetCacheHandle` and returned to higher filesystem read paths as the cache-backed reader.

## Risks And Edge Cases
Key risks include stale file-info cache entries after eviction, generation mismatch during reads, local file truncation causing short reads, random reads unintentionally starting downloads, and parallel-download mode changing wait behavior. Sparse mode assumes `fileDownloadJob` is non-nil before calling `HandleSparseRead`; malformed sparse handles could panic. The rapid unfinalized-object check is offset-only and comments acknowledge a possible edge around `offset+len(dst)`.

## Test Signals
`cache_handle_test.go` covers validation, sequential detection, job-status decisions, LRU recency changes, random/sequential reads, nil job behavior, file-info invalidation/generation mismatch, partial EOF handling, cache hit transitions, and parallel-download fallback behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle_test.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle_test.go

## Purpose
This suite specifies `CacheHandle` read decisions against a fake storage bucket and local cache directory. It validates handle invariants, sequential/random classification, downloader job interactions, file-info cache validation, LRU recency updates, cache-hit reporting, and parallel-download fallback behavior.

## Important APIs, Types, And Functions
`cacheHandleTest` sets up fake storage, a test object, an LRU file-info cache, a local cache file, a downloader job, and a `CacheHandle`. Helpers `addTestFileInfoEntryInCache` and `verifyContentRead` populate metadata and verify local file contents/permissions.

Tests call private helpers (`validateCacheHandle`, `shouldReadFromCache`, `validateEntryInFileInfoCache`) and public methods (`Read`, `IsSequential`, `Close`). They also construct downloader jobs with different `cfg.FileCacheConfig` values to test parallel-download behavior.

## Control Flow And State
Validation tests assert nil file handles and nil file-info caches fail, while nil download jobs are allowed. Sequential tests show backward offsets and gaps larger than `downloader.ReadChunkSize` switch to random behavior.

`shouldReadFromCache` tests cover not-started jobs, failed/invalid jobs, completed jobs, offsets less than/equal/greater than required offset, and job-status errors. File-info validation tests cover present entries, missing entries, generation mismatch, insufficient offset, and whether lookups do or do not change LRU order.

Read tests cover offset beyond object size, nil file handle, nil job with cache miss/hit, random reads with range caching on/off, sequential reads that wait for download, LRU order updates after reads, sequential-to-random transition, destination buffers longer than remaining content, cache entry removal, generation change, repeated reads where the second is a cache hit, and parallel-download configurations that force fallback instead of waiting.

## State And Persistence Behavior
The suite creates real local cache files under `$HOME/cache/dir` and removes them in teardown. It uses fake storage for object content and downloader jobs to populate the cache file. State assertions include job status offsets, cache hit booleans, LRU eviction order, local file permissions, and byte-for-byte content checks.

## Dependencies And Integration Points
Tests integrate fake storage, mocked storage control client, GCS bucket/object APIs, downloader jobs, LRU cache, cache util permissions/path helpers, metrics noop, tracing noop, semaphores, random data, and testify suite/assertions.

## Risks And Edge Cases
The suite highlights failures caused by stale metadata, generation changes after a read begins, local file short reads, and random reads with parallel downloads. Sparse-mode paths and rapid unfinalized-object fallback are not covered in this file, despite code branches in `Read`.

## Test Signals
Coverage is strong for non-sparse cache handle behavior with real local I/O and fake GCS. It gives both unit-level private helper coverage and integration-style read/download coverage.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handle_test.go -->

<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler.go -->
# sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler.go

## Purpose
`cache_handler.go` owns creation, lookup, invalidation, and cleanup of file-cache entries. It coordinates the file-info LRU cache, downloader job manager, local cache files, include/exclude regex policy, sparse-mode metadata, and cache-handle construction under a lock.

## Important APIs, Types, And Functions
`CacheHandler` stores the file-info cache, downloader `JobManager`, cache directory, file/dir permissions, a `locker.Locker`, compiled include/exclude regexes, sparse-mode flag, and volume block size. Public functions and methods include `NewCacheHandler`, `GetCacheHandle`, `InvalidateCache`, `Destroy`, and `shouldExcludeFromCache`. Private helpers include `compileRegex`, `createLocalFileReadHandle`, `cleanUpEvictedFile`, and `addFileInfoEntryAndCreateDownloadJob`.

## Control Flow And State
`NewCacheHandler` compiles regex filters and initializes the locker. Invalid regex strings are logged and ignored. `createLocalFileReadHandle` maps bucket/object names to a cache path and opens/creates it read-only with configured permissions.

`cleanUpEvictedFile` validates the cache key, invalidates/removes the corresponding download job, and truncates/removes the local cache file, ignoring missing files. `addFileInfoEntryAndCreateDownloadJob` builds the file-info key, checks for an existing entry, verifies the local file still exists, invalidates old entries when generation differs or the job is failed/invalid/missing before full download, inserts new `FileInfo`, creates a downloader job, and cleans up any LRU evictions. In sparse mode it sets `Offset` to `MaxUint64` and initializes `DownloadedChunks` with the job manager's download chunk size.

`GetCacheHandle` locks the handler, applies regex exclusion, skips cache creation for non-sparse random reads when range caching is disabled and no entry exists, ensures file-info/job state, creates a local file read handle, and returns a `CacheHandle` with the current job. `InvalidateCache` erases a specific entry and performs cleanup. `Destroy` invalidates all jobs through the job manager.

## State And Persistence Behavior
The handler mutates in-memory LRU metadata and downloader job state, and it creates/truncates/removes local cache files under `cacheDir`. LRU evictions trigger cleanup of both local file and job. Sparse mode persists partial object bytes in the same local file but accounts downloaded chunks through `FileInfo.DownloadedChunks`.

## Dependencies And Integration Points
The file integrates `data.FileInfo`/`FileSpec`, downloader `JobManager`, LRU cache, cache util path and file helpers, `locker`, `logger`, regex/path standard libraries, and `gcs.Bucket`/`MinObject`. It is the factory for `CacheHandle` and the invalidation hook for filesystem changes/unmount.

## Risks And Edge Cases
Correctness depends on holding `chr.mu` around cache/job/file transitions. Existing file-info entries with missing local files cause errors instead of self-healing in that path. Generation comparison cannot rely on monotonicity, so any mismatch invalidates. Regex exclusion uses `path.Join(bucket.Name(), bucket.GCSName(object))`, so policy patterns must match that joined form. Sparse random reads always create handles even when range caching is disabled.

## Test Signals
No `cache_handler_test.go` is part of this work item, but `cache_handle_test.go` and data tests cover consumers and metadata. Direct risks around regex filtering, eviction cleanup, sparse initialization, and missing-file behavior should be covered by separate cache-handler tests elsewhere.
<!-- END_FILE_RESEARCH: sources/user-network-fs/gcsfuse/internal/cache/file/cache_handler.go -->
