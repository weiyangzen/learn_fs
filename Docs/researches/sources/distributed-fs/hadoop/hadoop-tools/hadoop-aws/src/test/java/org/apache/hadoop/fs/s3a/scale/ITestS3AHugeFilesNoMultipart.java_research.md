<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java


## Purpose
Huge-file variant that disables multipart uploads and verifies single-PUT behavior and disabled multipart copy.


## Important APIs, Types, and Functions
ITestS3AHugeFilesNoMultipart overrides getBlockOutputBufferName(), expectMultipartUpload(), createScaleConfiguration(), and test_030_postCreationAssertions(). It configures CONNECTION_EXPECT_CONTINUE, IO_CHUNK_BUFFER_SIZE, MIN_MULTIPART_THRESHOLD, MULTIPART_SIZE, MULTIPART_UPLOADS_ENABLED, PART_UPLOAD_TIMEOUT, and REQUEST_TIMEOUT.


## Control Flow
Inherited huge-file workflow runs with disk buffering but no multipart upload. Post-creation assertions additionally confirm S3A internals report multipart copy disabled.


## State and Persistence Behavior
Persistent state is a single PUT-created large object, not MPU parts. Configuration state is deliberately stripped of base/bucket overrides to prevent accidental multipart behavior.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles, S3A internals, and S3AConstants around multipart and request timeouts.


## Risks and Test Signals
Risk is very long single PUT runtime and provider limits. The class is important for fail-fast validation when transfer manager would otherwise assume multipart thresholds.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesNoMultipart.java -->
