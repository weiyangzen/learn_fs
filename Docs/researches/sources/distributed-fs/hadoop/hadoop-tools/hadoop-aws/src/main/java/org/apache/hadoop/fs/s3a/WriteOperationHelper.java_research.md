# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/WriteOperationHelper.java

## Purpose
`WriteOperationHelper` is the concrete internal S3A write facade behind `WriteOperations`. It centralizes low-level S3 write calls, multipart upload lifecycle calls, retry translation, audit span activation, and callback integration with `S3AFileSystem`.

## Important APIs and control flow
The class owns an `S3AFileSystem`, an `Invoker` configured with `S3ARetryPolicy`, the store bucket, statistics context, `RequestFactory`, and a current `AuditSpan`. `retry()` activates the span and delegates to `Invoker.retry`. `createPutObjectRequest()` builds put requests through `RequestFactory`. Multipart flow is split across `initiateMultiPartUpload()`, `newUploadPartRequestBuilder()`, `uploadPart()`, `completeMPUwithRetries()` or `commitUpload()`, and abort helpers. `finalizeMultipartUpload()` validates that at least one completed part exists, builds `CompleteMultipartUploadRequest`, and calls `WriteOperationHelperCallbacks.completeMultipartUpload()`. Direct PUT calls route through `owner.putObjectDirect()`. Revert deletes the committed object key through `owner.deleteObjectAtPath()`.

## State, dependencies, and integration
State is mostly immutable construction-time wiring, plus the mutable `auditSpan` reference that is activated and deactivated by `close()`. The class depends on AWS SDK v2 S3 request/response models, Hadoop retry annotations, `Invoker`, `RequestFactory`, `PutObjectOptions`, `DurationTrackerFactory`, and S3A callbacks. Integration points are `S3AFileSystem` owner methods, `WriteOperationHelperCallbacks` for upload part and complete MPU, and audit spans created through `AuditSpanSource`.

## Risks and test signals
Risk centers on idempotency flags for retried S3 mutations, completion with missing parts, abort semantics when uploads are already absent, and preserving audit span context around callbacks. Tests should cover retry callback increments, empty part-list rejection, abort-without-retry vs retry paths, request factory use, direct put duration tracking, and `close()` deactivating spans without swallowing write failures.
