# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperations.java

## Purpose
`WriteOperations` is the internal S3A interface for write-side store operations. It hides concrete `WriteOperationHelper` details from stream, commit, and multipart code while still exposing retry, audit span creation, direct PUT, MPU, abort, and write-counter operations.

## Important APIs and control flow
The interface extends `AuditSpanSource` and `Closeable`, so write clients can create spans and release helper-scoped span state. It defines generic `retry()`, `createPutObjectRequest()`, write success/failure hooks, `initiateMultiPartUpload()`, `completeMPUwithRetries()`, abort overloads, `abortMultipartUploadsUnderPath()`, `listMultipartUploads()`, `abortMultipartCommit()`, `newUploadPartRequestBuilder()`, `putObject()`, `revertCommit()`, `commitUpload()`, `uploadPart()`, `getConf()`, and `incrementWriteOperations()`.

## State, dependencies, and integration
There is no state in the interface, but its contract implies implementors must coordinate Hadoop `Configuration`, AWS SDK v2 S3 models, `PutObjectOptions`, `S3ADataBlocks.BlockUploadData`, `DurationTrackerFactory`, and `Invoker.Retried`. It is a Limited internal boundary used by S3A output streams and committer logic.

## Risks and test signals
The interface encodes retry expectations through annotations; implementation drift can cause unexpected duplicate writes or missing retry translation. Tests should use mocks/fakes implementing this interface to verify stream code calls MPU operations in the right order, propagates `IOException`, and closes helpers after completion or failure.
