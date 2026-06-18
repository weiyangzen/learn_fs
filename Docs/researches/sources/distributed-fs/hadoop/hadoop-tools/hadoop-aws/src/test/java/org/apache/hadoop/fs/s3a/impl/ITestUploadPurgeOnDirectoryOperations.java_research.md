# Research: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/impl/ITestUploadPurgeOnDirectoryOperations.java

## Purpose
`ITestUploadPurgeOnDirectoryOperations` verifies that directory delete and rename operations abort pending multipart uploads beneath the affected directory when `DIRECTORY_OPERATIONS_PURGE_UPLOADS` is enabled.

## Important APIs, Types, and Functions
- Extends `AbstractS3ACostTest` for operation-cost assertions.
- `createConfiguration()` enables upload purge and magic committer support after clearing overrides.
- `setup()` assumes multipart support, asserts purge capability on root, and clears uploads under the method path.
- `testDeleteWithPendingUpload()` creates a magic upload under a directory, deletes the directory, and checks abort/list metrics.
- `testRenameWithPendingUpload()` creates a magic upload under a source directory, renames it, and checks the same purge behavior.
- `listUploads()` uses `StoreContext.pathToKey()` and `listUploadsUnderPrefix()` inside an audit span.

## Control Flow
Each active test creates a magic file, asserts one pending upload, runs delete or rename through `verifyMetrics()`, and asserts upload count returns to zero. Expected metrics include one aborted multipart upload and one underlying multipart upload list HTTP request.

## State and Persistence Behavior
Persistent S3 multipart upload state is intentionally created then purged. Real object state is limited to method-specific paths. Metrics are observed through inherited cost-validation state.

## Dependencies and Integration Points
The class integrates directory operations, pending multipart upload enumeration/abort, magic committer test utilities, S3A path capabilities, audit spans, and S3A statistics such as `OBJECT_MULTIPART_UPLOAD_ABORTED`.

## Risks and Edge Cases
Requires multipart upload support. External pending uploads under the same prefix would alter counts, hence setup clears the path. Metric names distinguish API-level list calls from HTTP object multipart list calls, which can be easy to confuse.

## Test Signals
Passing confirms delete and rename purge pending uploads under their source prefixes and emit the expected abort/list statistics.
