# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSInputStream.java

## Purpose
`OSSInputStream` reads Aliyun OSS objects through ranged requests and plugs into Alluxio's multi-range object stream abstraction.

## Important APIs, Types, And Functions
It extends `MultiRangeObjectInputStream`. Constructors accept bucket, key, `OSS` client, optional start position, retry policy, and range chunk size. `createStream(long startPos, long endPos)` builds `GetObjectRequest`, sets an inclusive OSS range, retries `NoSuchKey`, and returns a buffered object content stream.

## Control Flow
Construction fetches object metadata to cache content length. Range reads clamp the requested end to `contentLength - 1` because OSS may return the whole object when reading past the end. Non-`NoSuchKey` OSS errors fail immediately as `IOException`; missing keys retry according to a copied retry policy.

## State And Persistence
The stream keeps bucket, key, client, current `mPos` from the parent, cached object length, and retry policy. No data is persisted outside the remote read stream.

## Dependencies And Integration Points
It depends on Aliyun OSS SDK request/object/metadata types and Alluxio retry/multi-range infrastructure. `OSSUnderFileSystem.openObject` constructs it.

## Risks
Metadata lookup during construction can fail before retry handling. Zero-length objects need careful range boundaries. Eventual consistency is only retried for `NoSuchKey`.

## Test Signals
`OSSInputStreamTest` validates close, byte reads, buffer reads, and skip by mocking range-start-specific OSS responses.
