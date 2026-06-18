# sources/distributed-fs/alluxio/underfs/tos/src/main/java/alluxio/underfs/tos/TOSInputStream.java

## Purpose
`TOSInputStream` implements ranged reads from TOS using Alluxio's `MultiRangeObjectInputStream`, including retry behavior for eventually consistent not-found responses.

## APIs and Control Flow
Constructors store bucket, key, client, retry policy, initial position, and multi-range chunk size. They perform a `headObject` call to capture content length. `createStream(startPos, endPos)` builds a `GetObjectV2Input` with range options, clamps the end offset to `mContentLength - 1`, copies the retry policy, and repeatedly calls `getObject`. Non-404 TOS errors are thrown immediately as `IOException`; 404 errors are retried until policy exhaustion.

## State, Dependencies, and Integration
Runtime state includes bucket, key, `TOSV2` client, object length, and retry policy. It is created by `TOSUnderFileSystem.openObject`. It depends on Volcengine SDK request/response types, Apache `HttpStatus`, and Alluxio range-stream machinery.

## Risks and Test Signals
The implementation assumes `headObject` succeeds and does not wrap its exceptions locally. Empty objects can produce a range ending at `-1`. Test setup mocks range strings such as `bytes=0-`, but the implementation clamps against content length from `headObject`, so realistic range behavior depends on metadata mocking. `TOSInputStreamTest` covers close, sequential reads, byte-array reads, and skip.
