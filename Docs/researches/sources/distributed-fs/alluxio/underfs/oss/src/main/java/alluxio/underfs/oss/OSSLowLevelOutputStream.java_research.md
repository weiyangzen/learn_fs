# sources/distributed-fs/alluxio/underfs/oss/src/main/java/alluxio/underfs/oss/OSSLowLevelOutputStream.java

## Purpose
`OSSLowLevelOutputStream` implements streaming multipart uploads to Aliyun OSS for Alluxio object writes.

## Important APIs, Types, And Functions
It extends `ObjectLowLevelOutputStream` and implements provider-specific hooks: `initMultiPartUploadInternal`, `uploadPartInternal`, `completeMultiPartUploadInternal`, `abortMultiPartUploadInternal`, `createEmptyObject`, `putObject`, and `getContentHash`.

## Control Flow
The parent buffers data into partition-sized temp files. This subclass starts an OSS multipart upload, uploads each part with optional MD5, stores `PartETag`s, completes with all tags, or aborts on failure. Small or empty writes use `putObject`.

## State And Persistence
State includes the OSS client, synchronized part tag list, volatile upload id, and final ETag content hash. Temporary file state is managed by the parent stream.

## Dependencies And Integration Points
It depends on `ObjectLowLevelOutputStream`, Aliyun OSS multipart requests/results, Alluxio configuration partition size, and a `ListeningExecutorService` supplied by `OSSUnderFileSystem`.

## Risks
Part ordering relies on the collected tag list matching OSS expectations under concurrent uploads. Error paths translate SDK exceptions to `IOException`, but cleanup/abort reliability depends on the parent lifecycle.

## Test Signals
`OSSLowLevelOutputStreamTest` verifies small-file put, large-file multipart initiation/upload/completion, empty file creation, flush waiting, and content hash propagation.
