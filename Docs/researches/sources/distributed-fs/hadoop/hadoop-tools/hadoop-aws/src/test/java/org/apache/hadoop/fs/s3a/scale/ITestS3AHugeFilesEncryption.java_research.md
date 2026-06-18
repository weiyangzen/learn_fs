<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java


## Purpose
Huge-file scale test for SSE-KMS or DSSE-KMS encryption settings.


## Important APIs, Types, and Functions
ITestS3AHugeFilesEncryption overrides setup(), getBlockOutputBufferName(), isEncrypted(), and assertEncrypted(). It uses EncryptionTestUtils, getEncryptionAlgorithm(), and getS3EncryptionKey().


## Control Flow
setup() skips unless configured for SSE_KMS or DSSE_KMS. Inherited huge-file operations run with array buffering, then encryption assertions fetch the configured bucket key/algorithm and validate object metadata.


## State and Persistence Behavior
State is S3 encrypted object metadata and configured KMS key binding. The class reads fresh Configuration instances to inspect bucket encryption settings rather than storing them.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3A encryption utilities, bucket-specific config, and EncryptionTestUtils metadata checks.


## Risks and Test Signals
Risks include mismatched bucket KMS policy, missing encryption key, or incompatible mandatory bucket encryption. Test signals validate that large multipart objects preserve expected encryption metadata.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesEncryption.java -->
