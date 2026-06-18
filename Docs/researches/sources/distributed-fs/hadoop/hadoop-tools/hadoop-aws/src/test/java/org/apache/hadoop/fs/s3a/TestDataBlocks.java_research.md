# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestDataBlocks.java

## Purpose

Parameterized unit test for `S3ADataBlocks` upload buffer implementations: disk, byte array, and direct byte buffer. It validates block writes, upload content providers, stream mark/reset behavior, and buffer lifecycle.

## Important APIs, Types, and Functions

The test creates `DiskBlockFactory`, `ArrayBlockFactory`, or `ByteBufferBlockFactory`, then uses `DataBlock.write()`, `dataSize()`, `remainingCapacity()`, `hasCapacity()`, `startUpload()`, `BlockUploadData.getContentProvider()`, and `UploadContentProviders.BaseContentProvider.newStream()`.

## Control Flow

For each buffer type, a 128-byte block is created and loaded with `"test data"`. The content stream is read by single-byte and array reads, `available()` is checked throughout, mark/reset is exercised, a second stream is requested to ensure the first byte-buffer stream closes, and closing the block returns pooled buffers. After block close, creating another stream must fail.

## State, Dependencies, and Integration Points

State includes temporary disk files for disk buffering, in-memory arrays/byte buffers, content provider stream creation counts, and byte-buffer outstanding counts. It depends on contract byte helpers, `ByteBufferInputStream`, temporary directories, and AssertJ.

## Risks and Test Signals

This catches regressions in upload-body replayability, mark/reset support required by AWS request bodies, stream closure, byte-buffer pool leaks, and capacity accounting. Disk behavior is less deeply inspected than byte-buffer outstanding counts.
