# sources/distributed-fs/alluxio/underfs/s3a/src/main/java/alluxio/underfs/s3a/S3ALowLevelOutputStream.java

## Purpose
`S3ALowLevelOutputStream` provides streaming multipart uploads to S3.

## Important APIs, Types, And Functions
It extends `ObjectLowLevelOutputStream` and implements multipart hooks for initiate, upload part, complete, abort, small/empty put, and content hash retrieval. It supports server-side encryption metadata when configured.

## Control Flow
The parent stream buffers chunks and schedules uploads. This subclass starts an AWS multipart upload, uploads part files with optional MD5, accumulates `PartETag`s, completes multipart upload to receive an ETag, or aborts by upload id. Small writes use `putObject`.

## State And Persistence
State includes AWS client, synchronized part tag list, upload id, optional content hash, and SSE flag. Remote persistence occurs in S3 objects and multipart upload sessions.

## Dependencies And Integration Points
It depends on AWS SDK v1 multipart request/result classes, Alluxio object low-level streaming, and S3 partition-size configuration.

## Risks
Concurrent part completion ordering and tag list ordering are critical. Server-side encryption changes metadata for put/initiate paths and must stay aligned with provider requirements.

## Test Signals
`S3ALowLevelOutputStreamTest` covers small and large writes, multipart lifecycle, flush, empty object, close, and ETag propagation with mocked AWS calls.
