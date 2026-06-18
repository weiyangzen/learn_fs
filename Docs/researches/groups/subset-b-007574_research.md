# Research: subset-b-007574

Grouped research report for Hadoop S3A source files. Each file section is wrapped with the exact reconciliation markers required by the subset worker contract.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3A.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3A.java

## Purpose

`S3A` is the Hadoop `AbstractFileSystem`/`FileContext` adapter for the S3A connector. It does not implement S3 operations itself; it extends `DelegateToFileSystem` and delegates all real filesystem behavior to a new `S3AFileSystem` instance. Its role is to expose S3A through the newer `FileContext` API while preserving the scheme and lifecycle expectations of Hadoop filesystems.

## Important APIs, Types, and Functions

- `public class S3A extends DelegateToFileSystem`: public, evolving adapter class.
- `S3A(URI theUri, Configuration conf)`: constructs a `DelegateToFileSystem` with a new `S3AFileSystem`, using `Constants.FS_S3A` when the URI scheme is empty and otherwise preserving the URI scheme.
- `getUriDefaultPort()`: delegates to the superclass. The source leaves a commented-out direct S3A default port return, so this class intentionally follows the base delegate behavior.
- `toString()`: includes `fsImpl.getUri()` and the delegated implementation in diagnostics.
- `finalize()`: closes `fsImpl` before calling `super.finalize()`.

## Control Flow

Construction is the only significant path. The constructor immediately creates an `S3AFileSystem` and passes it into `DelegateToFileSystem`, so all later filesystem operations flow through the delegated `fsImpl`. There is no request handling, path translation, or S3-specific operation logic in this file.

When the JVM finalizer runs, the adapter calls `fsImpl.close()` as a best-effort cleanup path. This is a fallback lifecycle path, not a deterministic close API for `FileContext`.

## State and Persistence Behavior

The class keeps no fields of its own. State is inherited from `DelegateToFileSystem`, especially `fsImpl`. Persistent S3 state is not modified here except indirectly when delegated operations are invoked through `S3AFileSystem`. The finalizer can close client resources, thread pools, and other state owned by `S3AFileSystem`.

## Dependencies and Integration Points

- Hadoop `DelegateToFileSystem` is the integration point with `AbstractFileSystem` and `FileContext`.
- `S3AFileSystem` is the concrete implementation that performs all S3A behavior.
- `Configuration` and `URI` provide Hadoop initialization inputs.
- `Constants.FS_S3A` supplies the fallback scheme.

## Risks and Edge Cases

- `finalize()` based cleanup is nondeterministic and finalization is deprecated in modern Java runtimes. Correct resource cleanup should still happen through explicit filesystem lifecycle management where available.
- The constructor always creates a fresh `S3AFileSystem`; failures in S3A initialization surface during delegated filesystem initialization rather than through logic in this adapter.
- Empty-scheme URIs are normalized to `s3a`, but non-empty schemes are preserved. Any alias scheme support depends on the rest of Hadoop's filesystem registration and the delegated implementation.

## Test Signals

No direct test file was found for this adapter in the sampled references. Useful signals are indirect: any `FileContext` contract tests using the `s3a` scheme exercise this adapter, while most operation behavior is covered at the `S3AFileSystem` layer. Regression tests should check URI scheme selection, delegated close behavior, and `FileContext` construction against an S3A URI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3A.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ABlockOutputStream.java -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ABlockOutputStream.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ADataBlocks.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ADataBlocks.java

## Purpose

`S3ADataBlocks` defines the local buffering layer used by `S3ABlockOutputStream`. It abstracts three upload buffer strategies - heap byte arrays, direct `ByteBuffer`s, and temporary disk files - behind a common `DataBlock` state machine. Each block accepts bytes while in `Writing`, transitions to `Upload` to produce replayable `BlockUploadData`, and then transitions to `Closed` for resource cleanup.

## Important APIs, Types, and Functions

- `static void validateWriteArgs(byte[] b, int off, int len)`: delegates standard `OutputStream.write()` argument validation to `DataBlocks`.
- `static BlockFactory createFactory(StoreContext owner, String name)`: maps S3A configuration values to `ArrayBlockFactory`, `DiskBlockFactory`, or `ByteBufferBlockFactory`; throws for unknown buffer names.
- `BlockUploadData`: closeable wrapper around an `UploadContentProviders.BaseContentProvider<?>`. It can be built from a content provider, file, byte array slice, or whole byte array, and reports the provider size.
- `abstract BlockFactory`: owns the `StoreContext` and creates `DataBlock` instances with a block index, capacity limit, and output statistics.
- `abstract DataBlock`: common state machine with `DestState {Writing, Upload, Closed}`, `dataSize()`, `hasCapacity()`, `remainingCapacity()`, `write()`, `flush()`, `startUpload()`, `close()`, and block allocation/release statistics hooks.
- `ArrayBlockFactory` and `ByteArrayBlock`: allocate heap storage through `S3AByteArrayOutputStream`, avoid copying by exposing the underlying buffer, and upload through a byte-array content provider.
- `ByteBufferBlockFactory` and `ByteBufferBlock`: allocate direct buffers from `DirectBufferPool`, expose outstanding-buffer count for tests, upload through byte-buffer content providers, and return buffers to the pool on close.
- `DiskBlockFactory` and `DiskBlock`: create temp files through `StoreContext.createTempFile()` or a test-supplied function, stream writes to `BufferedOutputStream`, and upload through file content providers.

## Control Flow

`S3AFileSystem` chooses a block factory from `fs.s3a.fast.upload.buffer` configuration. `S3ABlockOutputStream` asks the factory for a new block whenever no active block exists, then writes into that block until capacity is exhausted or the stream closes.

The common write path starts in `DataBlock.write()`, which verifies the block is still in `Writing` and validates buffer bounds. Subclasses then write only up to `remainingCapacity()` and return the actual byte count. The caller is responsible for allocating a new block for any remainder.

`startUpload()` is the transition boundary. The base implementation moves state from `Writing` to `Upload`. Subclasses then freeze the current size and create content providers:

- `ByteArrayBlock` captures `buffer.size()`, keeps a reference to the underlying byte array, nulls the output stream, and returns a byte-array content provider guarded by `isUploading()`.
- `ByteBufferBlock` calculates used capacity and returns a byte-buffer content provider guarded by `isUploading()`.
- `DiskBlock` flushes and closes the local output stream, then returns a file content provider guarded by `isUploading()`.

Close flow is resource-specific. The base `close()` transitions to `Closed` once and calls `innerClose()`. Byte-array blocks drop the heap buffer reference. Byte-buffer blocks return the direct buffer to the pool. Disk blocks delete the temp file when upload did not start or when the block reaches the closed cleanup path.

## State and Persistence Behavior

`DataBlock` state is local and in-memory. It prevents writes after upload starts and content-provider creation after block close. Block allocation and release are reported to `BlockOutputStreamStatistics`.

No S3 persistence happens in this file. Persistence begins only when `S3ABlockOutputStream` passes `BlockUploadData` to `WriteOperations`. Local persistence can happen for `DiskBlock`, where bytes are stored in a temp file until the upload provider reads them and close cleanup deletes the file.

Resource ownership differs by backend:

- Array blocks hold JVM heap proportional to block size and queued upload backlog.
- ByteBuffer blocks hold direct memory from `DirectBufferPool` until the block closes.
- Disk blocks hold a filesystem temp file and file descriptor while writing, then a temp file while uploading.

The `isOpen`/`isUploading` suppliers passed to content providers are important: tests expect providers to reject new streams after the block is closed, protecting against stale re-reads of released buffers or deleted files.

## Dependencies and Integration Points

- `S3ABlockOutputStream` is the primary consumer.
- `StoreContext` supplies temp-file creation and filesystem context for disk buffering.
- `Constants.FAST_UPLOAD_BUFFER_ARRAY`, `FAST_UPLOAD_BUFFER_DISK`, and `FAST_UPLOAD_BYTEBUFFER` are the configuration names accepted by `createFactory()`.
- `UploadContentProviders` produces replayable content providers for AWS SDK request bodies.
- `DirectBufferPool` backs off-heap byte-buffer allocation.
- `BlockOutputStreamStatistics` receives block allocation/release signals.
- `DataBlocks.validateWriteArgs` centralizes standard stream argument checking.

## Risks and Edge Cases

- Heap array buffering can consume large amounts of memory when writes outpace multipart upload completion.
- Direct byte-buffer buffering moves pressure off heap but still needs strict close behavior to return buffers to the pool.
- Disk buffering depends on temp file creation and deletion. Failed deletion leaves local files behind; the class logs but cannot guarantee cleanup.
- `DiskBlock.innerClose()` has state-dependent behavior: while in `Upload`, it does not delete immediately because the file may still be read by the content provider; deletion occurs through later close paths.
- Blocks cap array and byte-buffer limits at `Integer.MAX_VALUE`; very large configured part sizes cannot produce larger single in-memory buffers.
- A disk block can be created with limit `-1` for unlimited single-PUT buffering when multipart upload is disabled; this can create very large local temp files.
- Content providers rely on block state predicates. Changes to state transitions can break mark/reset, retry, or replay behavior during AWS SDK uploads.

## Test Signals

`TestDataBlocks` parameterizes the disk, array, and bytebuffer factories. It verifies write size/capacity accounting, transition to upload, content provider stream creation counts, mark/reset behavior, byte-buffer stream state, full readback, old stream closure when a new stream is created, buffer release on block close, and rejection of new streams after close.

`ITestS3ABlockOutputArray`, `ITestS3ABlockOutputDisk`, and `ITestS3ABlockOutputByteBuffer` exercise these block implementations through real S3A output streams. They validate zero-byte and regular uploads, write-after-close failure, block allocation counters returning to zero, mark/reset, and abort behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ADataBlocks.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AEncryptionMethods.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AEncryptionMethods.java

## Purpose

`S3AEncryptionMethods` centralizes the encryption algorithm names accepted by S3A configuration and records whether each method is server-side and whether it requires a secret in the encryption key property. It gives the rest of S3A a typed enum instead of stringly-typed encryption checks.

## Important APIs, Types, and Functions

- Enum values:
  - `NONE("", false, false)`
  - `SSE_S3("AES256", true, false)`
  - `SSE_KMS("SSE-KMS", true, false)`
  - `SSE_C("SSE-C", true, true)`
  - `CSE_KMS("CSE-KMS", false, true)`
  - `CSE_CUSTOM("CSE-CUSTOM", false, true)`
  - `DSSE_KMS("DSSE-KMS", true, false)`
- `UNKNOWN_ALGORITHM`: stable error prefix used by tests and callers.
- `getMethod()`: returns the configuration/S3 algorithm string.
- `isServerSide()`: distinguishes server-side encryption from client-side encryption.
- `requiresSecret()`: indicates whether a separate secret/key must be looked up.
- `static getMethod(String name)`: parses a case-insensitive method string, treats blank values as `NONE`, and throws `IOException` for unknown algorithms.

## Control Flow

Parsing is linear over enum values. Blank or whitespace-only input returns `NONE` through `StringUtils.isBlank()`. Otherwise the method string is compared case-insensitively against each enum's configured method value. Unknown values fail fast with `IOException`.

There is no mutation. Each enum instance stores immutable metadata supplied by the constructor.

## State and Persistence Behavior

The enum has no persistent state. It influences later persistence behavior indirectly: server-side values affect S3 request headers and client-side values affect encrypted client setup and upload handling. `requiresSecret()` is used by secret/delegation-token code to decide whether an encryption key must be present.

## Dependencies and Integration Points

- `S3AUtils.getEncryptionAlgorithm()` calls `S3AEncryptionMethods.getMethod()` while loading bucket-specific configuration and validating key requirements.
- `S3AFileSystem` uses the parsed algorithm to decide whether client-side encryption is enabled.
- `RequestFactory` exposes server-side encryption algorithm settings for request construction.
- `EncryptionSecrets` serializes/deserializes method strings for delegation token support.
- `EncryptionSecretOperations` validates SSE-C, SSE-KMS, and DSSE-KMS secret/context requirements.
- `S3ObjectAttributes` carries the server-side encryption method in object metadata.

## Risks and Edge Cases

- The parser accepts only `getMethod()` strings, not enum constant names. For example, callers must pass `SSE-KMS`, not necessarily `SSE_KMS`.
- Blank input silently maps to `NONE`; this is convenient for unset configuration but can hide accidental whitespace-only values.
- Adding a new encryption method requires updating downstream validation, request construction, secret handling, and tests, not just this enum.
- `requiresSecret()` is true for SSE-C and client-side encryption modes but false for KMS modes, where a KMS key id may be optional or configured separately depending on AWS behavior and S3A validation.

## Test Signals

Tests refer to `UNKNOWN_ALGORITHM` and exercise encryption parsing through `S3AUtils`, `EncryptionSecrets`, client-side encryption integration tests, and request factory setup. Useful regression coverage includes blank input, case-insensitive parsing, unknown algorithm error text, `isServerSide()` for CSE versus SSE methods, and `requiresSecret()` for SSE-C/CSE modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AEncryptionMethods.java -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileStatus.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileStatus.java

## Purpose

`S3AFileStatus` is the S3A-specific `FileStatus` implementation used for object and pseudo-directory metadata. It extends Hadoop's `FileStatus` with S3-specific eTag and version id fields and a tri-state "empty directory" marker so listing, rename, delete, auditing, and located-status conversion can reason about S3's directory emulation.

## Important APIs, Types, and Functions

- `public class S3AFileStatus extends FileStatus implements EtagSource`: exposes S3 eTag through the standard `EtagSource` interface.
- Directory constructors:
  - `S3AFileStatus(boolean isemptydir, Path path, String owner)`
  - `S3AFileStatus(Tristate isemptydir, Path path, String owner)`
- File constructor: `S3AFileStatus(long length, long modification_time, Path path, long blockSize, String owner, String eTag, String versionId)`.
- Package-private combined constructor: creates either file or directory status and calls the modern `FileStatus` superclass constructor with owner/group set to owner and directory flags.
- `static fromFileStatus(FileStatus source, Tristate isEmptyDirectory, String eTag, String versionId)`: converts a generic status into S3A status while preserving file metadata and adding S3 metadata.
- `isEmptyDirectory()` and `setIsEmptyDirectory()`: expose/update the tri-state directory emptiness marker.
- `getETag()` and `getEtag()`: deprecated S3A spelling plus standard interface spelling.
- `getVersionId()` and `setVersionId()`: expose/update S3 object version id.
- `getModificationTime()`: returns current time for directories and the stored modification time for files.
- `equals()` and `hashCode()`: explicitly defer to `FileStatus`, preserving path-based semantics.
- `toString()`: appends empty-directory, eTag, and version id information to the base status string.

## Control Flow

Construction splits along directory versus file paths. Directory statuses carry length, modification time, and block size as zero and use `Tristate` to represent empty, non-empty, or unknown emptiness. File statuses carry object length, object last-modified time, block size, eTag, and version id.

`fromFileStatus()` branches on `source.isDirectory()`. Directory conversion creates a directory status and does not preserve eTag/version id because pseudo-directories do not represent normal S3 object metadata in the same way. File conversion preserves length, modification time, path, block size, owner, eTag, and version id.

`getModificationTime()` intentionally changes directory behavior at read time: directories report `System.currentTimeMillis()` to avoid ecosystem components treating stale marker object timestamps as old directories.

## State and Persistence Behavior

The class is serializable through `FileStatus` and adds mutable fields:

- `Tristate isEmptyDirectory`
- `String eTag`
- `String versionId`

It does not perform persistence itself. The fields mirror S3 object/listing/head metadata created elsewhere. `setVersionId()` and `setIsEmptyDirectory()` allow later operations to refine status metadata without reconstructing the object.

Directory modification time is intentionally non-stable because it returns the current local time on each call. This affects consumers that cache or compare directory status values.

## Dependencies and Integration Points

- `S3AUtils.createFileStatus()` and `createUploadFileStatus()` build instances from S3 metadata.
- `S3AFileSystem.innerGetFileStatus()`, `s3GetFileStatus()`, rename, delete, listing, and content-summary paths use `S3AFileStatus` to distinguish files, empty directories, non-empty directories, and unknown states.
- `Listing` creates iterators of `S3AFileStatus` from S3 object listings and common prefixes.
- `S3ALocatedFileStatus` copies eTag, version id, and empty-directory state and can convert back to `S3AFileStatus`.
- `DirMarkerTracker`, marker tools, audit managers, mkdir operations, and rename/delete operations inspect status metadata.
- `EtagSource` lets public APIs access eTags without relying on the deprecated `getETag()` method.

## Risks and Edge Cases

- Directory modification time is dynamic by design. Code expecting stable directory mtimes can see changing values across calls.
- Equality and hash code come from `FileStatus`, so eTag, version id, and empty-directory state do not affect equality. This is useful for path identity but risky for metadata-sensitive caches.
- `fromFileStatus()` drops eTag/version id for directories. If a directory marker object's own metadata matters, it must be carried elsewhere.
- `toString()` has nested `String.format()` calls that effectively place eTag and version id inside the formatted empty-directory suffix. This is diagnostic only but worth checking when changing it.
- Mutable `versionId` and `isEmptyDirectory` can diverge from actual S3 state if reused after object changes.

## Test Signals

Signals include:

- `TestS3AResourceScope`, which constructs directory and file statuses and verifies executable/scope behavior.
- `ITestS3AFileOperationCost`, which verifies `isEmptyDirectory()` for root, empty directories, non-empty directories, and file status probes.
- `TestS3AGetFileStatus`, which covers status creation from S3 object and listing metadata.
- Located-status tests and code paths through `S3ALocatedFileStatus` should preserve eTag/version id/empty-directory fields.
- Rename and mkdir integration tests indirectly validate the tri-state empty-directory behavior because overwrite and parent checks depend on it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AFileStatus.java -->
