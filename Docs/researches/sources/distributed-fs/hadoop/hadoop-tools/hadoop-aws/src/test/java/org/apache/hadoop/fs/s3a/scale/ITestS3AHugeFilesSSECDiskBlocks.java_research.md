<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java


## Purpose
Huge-file disk-buffer variant with SSE-C client-provided encryption enabled.


## Important APIs, Types, and Functions
ITestS3AHugeFilesSSECDiskBlocks overrides setup() and createScaleConfiguration(), sets S3_ENCRYPTION_ALGORITHM to SSE_C, and sets a fixed base64 SSE-C key.


## Control Flow
setup() runs the parent setup but skips if the bucket rejects SSE-C or encryption tests are disabled. The inherited disk-buffer huge-file suite then runs under SSE-C configuration.


## State and Persistence Behavior
State is encrypted S3 object metadata and local disk upload buffering. The fixed test key is configuration-only and not persisted by this class.


## Dependencies and Integration Points
Depends on ITestS3AHugeFilesDiskBlocks, S3AEncryptionMethods.SSE_C, skipIfEncryptionTestsDisabled(), and bucket encryption policies.


## Risks and Test Signals
Risks include 403 AccessDenied on mandatory-encryption buckets and provider support gaps. Test signals validate huge multipart operations with SSE-C and direct vector buffers.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesSSECDiskBlocks.java -->
