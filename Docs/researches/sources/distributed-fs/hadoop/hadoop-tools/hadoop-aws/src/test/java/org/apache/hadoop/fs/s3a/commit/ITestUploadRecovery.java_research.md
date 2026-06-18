# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/commit/ITestUploadRecovery.java

## Purpose
Integration tests for recovery from injected S3 SDK failures during simple PUT, magic multipart writes, and `CommitOperations` upload/complete flows. The class is parameterized over S3A fast-upload buffer implementations.

## Important APIs, Types, and Functions
The class extends `AbstractS3ACostTest` and uses `SdkFaultInjector` as an SDK execution interceptor. Parameters cover `FAST_UPLOAD_BUFFER_ARRAY`, `FAST_UPLOAD_BUFFER_DISK`, and `FAST_UPLOAD_BYTEBUFFER`, with the full commit test run only once. Key methods are `createConfiguration()`, `setup()`, `teardown()`, `testPutRecovery()`, `testMagicWriteRecovery()`, and `testCommitOperations()`.

## Control Flow and Behavior
Configuration removes bucket overrides, selects the fast-upload buffer, enables create performance mode, sets up teardown upload purging, and installs the fault injector. `testPutRecovery()` injects failures for PUT responses and expects a normal stream close to recover. `testMagicWriteRecovery()` writes to a magic path and injects upload-part failures; with client-side encryption enabled, retrying MPU is expected to throw, otherwise the write must recover. `testCommitOperations()` creates a local staged file, injects part upload failures, uploads it to a pending commit, then injects complete-MPU failures and either expects a `FileNotFoundException` if complete consumes the upload ID or a successful retry otherwise.

## State, Persistence, and Dependencies
State includes fault-injector counters/evaluators, local temp files, pending commit metadata, multipart upload IDs, and S3A filesystem configuration. The test depends on SDK interceptor behavior, S3 multipart semantics, `MULTIPART_COMMIT_CONSUMES_UPLOAD_ID`, and whether client-side encryption is active.

## Integration Points, Risks, and Test Signals
This suite is a targeted signal for retry safety around multipart uploads. It exercises S3A stream upload, magic pending writes, and committer upload/complete paths under transient failures. Risks include provider-specific behavior after failed complete-MPU requests, CSE incompatibility with MPU retry, and accidental persistence of fault injection into cleanup; teardown resets the injector to reduce that risk.
