<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java


## Purpose
Huge-file test that verifies configured S3 storage class is applied on create and rename/copy.


## Important APIs, Types, and Functions
ITestS3AHugeFilesStorageClass overrides createScaleConfiguration(), getBlockOutputBufferName(), selected inherited tests, assertStorageClass(), and skipQuietly(). It configures STORAGE_CLASS_REDUCED_REDUNDANCY.


## Control Flow
The class runs create/post-create storage-class assertions, skips read/encryption-only inherited checks, and overrides rename to copy the huge object then validate size and storage class at destination.


## State and Persistence Behavior
Persistent state is object metadata storageClassAsString() on the huge file and renamed destination. Filesystem caching is disabled so configuration changes are respected.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3AInternals.getObjectMetadata(), ContractTestUtils timers/bandwidth, and storage-class test skip helpers.


## Risks and Test Signals
Risks include provider support for Reduced Redundancy and metadata differences after copy. Signals catch storage-class loss across multipart upload and rename/copy.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesStorageClass.java -->
