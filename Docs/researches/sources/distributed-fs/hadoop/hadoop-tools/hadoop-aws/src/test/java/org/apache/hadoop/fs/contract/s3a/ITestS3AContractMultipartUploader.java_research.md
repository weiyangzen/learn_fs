# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractMultipartUploader.java

Purpose: S3A implementation of multipart uploader contract tests, gated as integration/scale tests.

Important APIs/types/functions: extends `AbstractContractMultipartUploaderTest`; `partSizeInBytes()` returns configured `partitionSize`; payload count is 3; concurrent uploads to the same path are supported; `finalizeConsumesUploadIdImmediately()` reflects `MULTIPART_COMMIT_CONSUMES_UPLOAD_ID`. Configuration disables checksum generation/algorithm and FS caching.

Control flow: setup requires scale tests, assumes multipart uploads, reads partition size and upload-ID consumption behavior, and logs checksum settings. Directory-in-way and reverse-order tests are skipped/assumed as S3-specific. Abort tolerates `FileNotFoundException` from third-party stores.

State and persistence: creates multipart uploads and objects in the test bucket; reads filesystem configuration for stateful behavior flags.

Dependencies and integration: multipart uploader contract, S3A checksum support, scale-test constants, and S3 Express assumptions.

Risks: scale tests are expensive and depend on store multipart support. Third-party stores may not expose aborted uploads consistently.

Test signals: scale integration coverage for multipart upload lifecycle, concurrency, finalize semantics, and abort tolerance.
