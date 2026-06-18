# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ABlockOutputStream.java

## Purpose

`S3ABlockOutputStream` is S3A's main write stream for normal object creation. It buffers writes into `S3ADataBlocks.DataBlock` instances and uploads them either as a single PUT or as multipart upload parts. It also coordinates committer-aware delayed visibility, magic output streams, client-side encryption final-part handling, abort support, stream capabilities, progress callbacks, and IO statistics.

The class is package-private and marked private/unstable because it sits at the boundary between Hadoop's `OutputStream` APIs and S3 multipart semantics. `S3AFileSystem` builds it during create operations and wraps it in `FSDataOutputStream`.

## Important APIs, Types, and Functions

- `class S3ABlockOutputStream extends OutputStream implements StreamCapabilities, IOStatisticsSource, Syncable, Abortable`: exposes Hadoop stream interfaces while deliberately not supporting real sync semantics.
- `S3ABlockOutputStream(BlockOutputStreamBuilder builder)`: validates dependencies, initializes multipart upload when required by `PutTracker` or write flags, configures progress/statistics, and creates the first block so open-close creates a zero-byte object.
- `write(int)` and `write(byte[], int, int)`: validate arguments, check open state, write into the active block, and trigger asynchronous part upload when a multipart-enabled block is full. With client-side encryption enabled, an exactly full final block is retained until close so the last-part flag can be supplied.
- `flush()`: flushes only the active local block. It does not make data visible or upload a partial block.
- `close()`: finalizes the upload. It chooses single PUT when no multipart upload was started, otherwise uploads any final part, waits for all part futures, gives `PutTracker` a chance to defer completion, completes the MPU when appropriate, records statistics, and cleans local resources.
- `abort()`: closes the stream and aborts any active multipart upload, returning an `AbortableResult` that distinguishes already-closed/no-op behavior from cleanup exceptions.
- `hasCapability(String)`: reports magic output, abortable stream, IO statistics, IO statistics context, write flags, and false for `hflush`/`hsync`.
- `hflush()` and `hsync()`: count invocations. `hflush()` is a no-op; `hsync()` either throws `UnsupportedOperationException` or logs/downgrades depending on configuration.
- Nested `MultiPartUpload`: owns the S3 upload id, futures for ordered `CompletedPart` results, active blocks needing cleanup, abort state, submitted/uploaded counters, and remembered upload failure.
- Nested `BlockUploadProgress`: translates PUT and multipart part events into statistics and downstream progress callbacks.
- Nested `BlockOutputStreamBuilder`: collects required construction dependencies, including key, block factory, block size, executor, write operations, put tracker, put options, statistics, encryption flag, thread IO statistics aggregator, and multipart-enabled flag.

## Control Flow

The stream is initialized through `S3AFileSystem.create`, where the filesystem supplies `blockFactory`, `partSize`, a `PutTracker`, `WriteOperationHelper`, `PutObjectOptions`, a semaphored executor, and multipart/encryption configuration. The constructor may immediately start an MPU if a committer tracker or create-file flag requires multipart output.

Write flow is synchronized around the active block:

1. Validate the buffer and closed state.
2. Allocate a block with `createBlockIfNeeded()` if there is no active block.
3. Write as much data as fits.
4. If multipart upload is disabled, retain all data in a single unlimited disk block.
5. If the write overflowed the current block, call `uploadCurrentBlock(false)` and recursively write the remainder.
6. If the block is exactly full and client-side encryption is not enabled, upload it asynchronously.

`uploadCurrentBlock()` initializes the MPU if needed, asks `MultiPartUpload` to queue the block, adds the block size to stream-level submitted byte accounting, and clears the active block so the next write allocates a new one.

Single PUT close flow is used when no MPU exists. `putObject()` converts the active block to `BlockUploadData`, creates a `PutObjectRequest`, records queued/start/complete/failure progress events, calls `WriteOperations.putObject`, and closes the upload data and block.

Multipart close flow uploads a final part when needed, waits for all futures in submission order, rejects stub parts with empty ETags, asks `PutTracker.aboutToComplete()` whether the MPU should be completed immediately, and then calls `completeMPUwithRetries()` through `WriteOperationHelper` when output should be visible. Magic and committer paths can upload parts without completing visibility until job commit.

Failure flow is conservative. IOException during close aborts the MPU if present, calls `writeOperationHelper.writeFailed()`, and rethrows. Cancellation while waiting for futures also aborts and is converted to `InterruptedIOException`. Cleanup always closes the active block, block factory, and statistics, and merges stream IO statistics into the thread aggregator.

## State and Persistence Behavior

The stream's local mutable state includes:

- `closed`: atomic guard for close and abort idempotence.
- `activeBlock`: the current local buffer, synchronized for mutations.
- `blockCount`: monotonically increasing block index. It logs an error at/above S3's multipart count limit.
- `multiPartUpload`: null until multipart upload starts; non-null owns the remote upload id.
- `bytesSubmitted`: stream-level bytes queued to S3.
- `statistics` and `iostatistics`: per-stream counters, durations, block allocation, transfer, abort, sync, and commit-upload metrics.

Remote persistence is delayed until S3 calls execute. For small non-multipart writes, the remote object is created only during `close()` through PUT, including zero-byte files. For multipart writes, parts are persisted as they are uploaded but the object is visible only after MPU completion. `PutTracker` may intentionally prevent immediate completion, shifting visibility to committer logic. `abort()` attempts to cancel futures and abort the remote MPU so uploaded parts do not remain billable.

Thread state matters. Multipart uploads run on the provided executor through a Guava `ListeningExecutorService`. The main stream waits for futures on close. Progress callbacks may happen on worker threads, and the class documentation warns callers that detailed `ProgressListener` events are cross-thread.

## Dependencies and Integration Points

- `S3ADataBlocks.BlockFactory`, `DataBlock`, and `BlockUploadData` provide array, direct-buffer, or disk upload data.
- `WriteOperations`/`WriteOperationHelper` encapsulate S3 requests, audit span activation, PUT, MPU initiation, part upload, complete, abort, and write success/failure notifications.
- AWS SDK v2 model types include `PutObjectRequest`, `UploadPartRequest`, `UploadPartResponse`, `CompletedPart`, and `RequestBody`.
- `PutTracker` integrates committers and magic output, deciding initial multipart behavior, completion metadata, and immediate visibility.
- `PutObjectOptions` and `WriteObjectFlags` carry headers, conditional overwrite/create flags, etag preconditions, and create-multipart requests.
- `ProgressListener` and `Progressable` bridge Hadoop progress with detailed transfer events.
- `BlockOutputStreamStatistics`, `IOStatisticsAggregator`, and statistic symbols provide instrumentation.
- `SemaphoredDelegatingExecutor` is supplied by `S3AFileSystem` to bound active block uploads.

## Risks and Edge Cases

- `flush()` does not upload or make data durable in S3. Applications assuming HDFS-like flush/sync persistence can lose data until `close()`.
- `hsync()` can be downgraded to a warning; this preserves compatibility but may hide unsafe application assumptions.
- Multipart failure handling depends on remembering the first async upload failure and rethrowing before completion. Races in asynchronous completion must preserve that invariant.
- The comment in `completeUpload()` notes that a fast future can finish before `addSubmission()` records the block in `blocksToClose`; the cleanup path tolerates this but resource accounting should be watched.
- `partsUploaded` and `blockUploadFailure` are mutated by worker threads without strong synchronization. They appear to be used for statistics/failure signaling rather than fine-grained coordination, but future changes should avoid relying on unsynchronized visibility.
- For CSE, exactly full blocks are not uploaded immediately because the final part must be flagged. This can increase memory/disk retention compared with non-CSE writes.
- The stream only logs when block count reaches the S3 multipart limit; the actual failure may occur later when building or submitting part requests.
- Abort is best effort. If S3 abort fails, the result carries the cleanup exception and logs that uploaded parts may need purging.
- `close()` blocks for all queued uploads and can be slow; callers rely on progress callbacks to avoid external timeouts.

## Test Signals

Relevant tests include:

- `TestS3ABlockOutputStream`: validates flush after closed stream is no-op, abort closes the stream, close-after-abort is harmless, `hsync()` rejection/downgrade behavior, and part-number limit enforcement through `WriteOperationHelper`.
- `ITestS3ABlockOutputArray`, `ITestS3ABlockOutputDisk`, and `ITestS3ABlockOutputByteBuffer`: exercise small uploads across buffer backends, zero-byte upload, write-after-close failure, block allocation release, mark/reset content provider behavior, and abort semantics.
- Scale tests such as huge-file block tests cover multipart behavior under larger writes and alternate buffer modes.
- Integration with `S3AFileSystem.create` is a key regression surface because builder wiring controls encryption, multipart availability, executor bounding, put tracking, and stream capabilities.
