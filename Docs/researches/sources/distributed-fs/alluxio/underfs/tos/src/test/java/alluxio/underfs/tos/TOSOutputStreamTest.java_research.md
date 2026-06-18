# sources/distributed-fs/alluxio/underfs/tos/src/test/java/alluxio/underfs/tos/TOSOutputStreamTest.java

## Purpose
This test suite validates `TOSOutputStream` delegation, upload close behavior, exception propagation, and content hash reporting.

## Important Tests
`testConstructor` forces `Files.newOutputStream` to throw and expects an `IOException`. `testWrite1`, `testWrite2`, and `testWrite3` verify writes reach the buffered local stream. `testCloseError` makes `putObject` throw a `TosException` and expects `AlluxioTosException`. `testCloseSuccess` verifies temp file deletion. `testFlush` verifies flush delegation. Successful tests assert that `getContentHash()` exposes the mocked ETag.

## Dependencies and Integration
The suite uses PowerMock to intercept constructors and static `Files` methods, Mockito for the TOS client, and Alluxio temp directory configuration.

## Signals and Gaps
The tests confirm the local-buffer upload design but do not exercise actual MD5 metadata generation, idempotent double close, temp file delete failure logging, or real filesystem writes.
