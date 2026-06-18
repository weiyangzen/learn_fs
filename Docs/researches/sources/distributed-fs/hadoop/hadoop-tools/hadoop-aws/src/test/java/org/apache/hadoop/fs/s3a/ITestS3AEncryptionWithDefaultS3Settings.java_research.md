# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AEncryptionWithDefaultS3Settings.java

Purpose: Tests existing S3 bucket default SSE-KMS settings without S3A explicitly setting encryption on initial writes. It verifies bucket-default encrypted objects and rename behavior when a second filesystem explicitly uses SSE-KMS.

Important APIs/types/functions: `patchConfigurationEncryptionSettings()`, `assertEncrypted()`, `skipIfBucketNotKmsEncrypted()`, `validateEncryptionFileAttributes()`, `EncryptionSecrets`, `FileSystem.newInstance()`, `S3AEncryptionMethods.NONE`, and `S3AEncryptionMethods.SSE_KMS`.

Control flow: setup skips unless encryption is configured. Base propagation/direct encryption tests are disabled. File-attribute and rename tests first create a probe object and inspect metadata to ensure the bucket default is `aws:kms`; then they write content, verify it, and assert encryption metadata and KMS key. Rename test uses a new filesystem configured with SSE-KMS to copy/rename the source into a target directory and verify the renamed file's encryption.

State and persistence: creates probe, source, and target objects/directories in S3; probe cleanup is in `finally`. No local persistent state.

Dependencies and integration points: bucket default encryption, S3 metadata, configured KMS key, S3A copy/rename encryption behavior, and encryption-file-attribute reporting.

Risks: environment-dependent and skip-heavy; inherited base tests are disabled by design; bucket default must match auth-keys KMS key; rename behavior can vary with copy implementation.

Test signals: validates compatibility with server-side bucket default SSE-KMS and S3A's ability to preserve/apply encryption during rename/copy.
