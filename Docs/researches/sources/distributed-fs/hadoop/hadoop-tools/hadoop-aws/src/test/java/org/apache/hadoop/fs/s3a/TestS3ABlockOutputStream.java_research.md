# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3ABlockOutputStream.java

## Purpose

Unit tests for `S3ABlockOutputStream` edge behavior around closed streams, abort semantics, multipart part-number validation, and `Syncable` downgrade behavior.

## Important APIs, Types, and Functions

The test builds `S3ABlockOutputStream.BlockOutputStreamBuilder` with mocked executor, progress callback, block factory, write helper, put tracker, put options, and IOStatistics aggregator. It uses `flush()`, `abort()`, `checkOpen()`, `write()`, `close()`, `hflush()`, `hsync()`, and `WriteOperationHelper.newUploadPartRequestBuilder()`.

## Control Flow

`setUp()` creates a spied stream from the mock builder. One test forces `checkOpen()` to throw and verifies `flush()` becomes a no-op when closed. Multipart limits are tested by building part 1 successfully and intercepting `PathIOException` for part 50000. Abort tests ensure abort closes the stream, write checks open state, and close after abort is harmless. Sync tests distinguish unsupported `hsync()` from configured downgrade.

## State, Dependencies, and Integration Points

State is local mock/spied stream state and a mocked `S3AFileSystem` request factory. It integrates output stream builder wiring, multipart request validation, audit noop support, write operation callbacks, and Hadoop `ClosedIOException`.

## Risks and Test Signals

Mocked builder pieces mean this tests stream contract edges rather than upload success. It catches part-limit regressions, abort/close idempotency issues, and accidental reintroduction of unsupported `hsync()` failures when downgrade is enabled.
