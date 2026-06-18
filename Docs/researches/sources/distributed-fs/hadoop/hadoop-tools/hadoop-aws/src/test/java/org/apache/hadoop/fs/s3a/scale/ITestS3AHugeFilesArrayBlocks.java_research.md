<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java


## Purpose
Concrete huge-file scale-test variant using in-memory array blocks for fast upload buffering.


## Important APIs, Types, and Functions
ITestS3AHugeFilesArrayBlocks overrides getBlockOutputBufferName() to return FAST_UPLOAD_BUFFER_ARRAY and requireMultipartUploads() to require MPU availability.


## Control Flow
All create/read/rename/delete control flow is inherited from AbstractSTestS3AHugeFiles; this class supplies the buffering mode and skip condition.


## State and Persistence Behavior
State is the inherited huge S3 object lifecycle plus array-backed upload block memory state. No additional fields are introduced.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles and S3A Constants.FAST_UPLOAD_BUFFER_ARRAY.


## Risks and Test Signals
Risk is high heap pressure for huge files; test signal isolates array-buffer multipart behavior from disk and bytebuffer variants.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesArrayBlocks.java -->
