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
