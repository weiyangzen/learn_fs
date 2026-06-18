# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestS3AUnbuffer.java

## Purpose

`TestS3AUnbuffer.java` is a mock-based unit test for the S3A input stream `unbuffer()` contract. It verifies that calling `FSDataInputStream.unbuffer()` on a stream opened from S3A closes the underlying AWS SDK `ResponseInputStream<GetObjectResponse>` object stream, not only Hadoop's wrapper layer.

## Important APIs, Types, and Functions

The single test method, `testUnbuffer()`, extends `AbstractS3AMockTest` and uses the mocked `s3` client and `fs` filesystem. It builds `HeadObjectResponse` and `GetObjectResponse` values, wraps a Mockito `InputStream` in `AbortableInputStream`, then in `ResponseInputStream<GetObjectResponse>`, and opens the path through `fs.open()`.

## Control Flow

The test installs `headObject` metadata for `getFileStatus()`, installs `getObject` data for `open()`, reads from the stream to force the S3 object stream into use, then calls `stream.unbuffer()`. Finally it verifies `objectStream.close()` was invoked at least once.

## State and Persistence Behavior

All state is in-memory Mockito state. There is no S3 persistence; metadata and object streams are synthetic. The important lifecycle state is that the active S3 object stream transitions from open to closed when Hadoop's unbuffer hook is called.

## Dependencies and Integration Points

The test integrates Hadoop `FSDataInputStream`, S3A stream construction, AWS SDK v2 S3 response streams, and Mockito. It explicitly skips when the analytics accelerator is enabled because that stream implementation does not support unbuffer.

## Risks and Edge Cases

The test depends on mocked end-of-stream reads and does not validate byte-range or partial-read cleanup. Its main regression target is resource leakage: if unbuffer stops propagating to the AWS stream, HTTP connections can stay held.

## Test Signals

Strong signal is `verify(objectStream, atLeast(1)).close()`. Supporting signals are successful mocked open/read and the analytics accelerator skip guard.
