<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java


## Purpose
Concrete huge-file scale-test variant using disk-backed upload blocks and direct buffers for vector IO.


## Important APIs, Types, and Functions
ITestS3AHugeFilesDiskBlocks overrides getBlockOutputBufferName() to FAST_UPLOAD_BUFFER_DISK and isDirectVectorBuffer() to true.


## Control Flow
The inherited huge-file workflow creates, verifies, reads, renames, and deletes a large object while this subclass changes upload buffering and vector-read buffer allocation.


## State and Persistence Behavior
State includes temporary disk block files managed by S3A upload buffering and persisted S3 huge-file objects. The class itself has no mutable fields.


## Dependencies and Integration Points
Depends on AbstractSTestS3AHugeFiles and S3A Constants.FAST_UPLOAD_BUFFER_DISK.


## Risks and Test Signals
Risks are local disk pressure and cleanup of temporary upload blocks. Test signals isolate disk-buffer behavior and direct vector buffer compatibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AHugeFilesDiskBlocks.java -->
