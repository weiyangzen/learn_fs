<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java


## Purpose
Integration tests for BucketTool bucket creation validation, especially S3 Express constraints, without intentionally creating new buckets.


## Important APIs, Types, and Functions
ITestBucketTool defines setup(), tests for recreating existing S3 Express/non-S3 Express buckets, zone argument validation, missing S3 Express zone, non-AWS endpoint rejection, and d().


## Control Flow
setup captures the active FS, bucket URI, region, S3 Express capability, and BucketTool. Tests invoke bucketTool.exec() with create/region/zone/endpoint arguments and assert AWS or launcher error codes/messages according to store type.


## State and Persistence Behavior
No intended persistent bucket creation; operations target existing test bucket or invalid sample names. State is per-test fields derived from current filesystem configuration.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, BucketTool constants, S3ATestUtils assumptions/error helpers, S3 Express capability, ExitUtil, and launcher exit codes.


## Risks and Test Signals
Risks are endpoint/region-specific errors and third-party stores behaving differently. Signals protect CLI validation around S3 Express zone requirements and provider safety checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/tools/ITestBucketTool.java -->
