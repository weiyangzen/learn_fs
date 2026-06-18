<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java


## Purpose
Scale test for multipart upload part-count limits, commit upload failure cleanup, and Abortable output-stream behavior.


## Important APIs, Types, and Functions
ITestS3AMultipartUploadSizeLimits overrides createScaleConfiguration() to set MULTIPART_SIZE=5 MiB and UPLOAD_PART_COUNT_LIMIT=2, then defines tests for two-part upload, over-limit failure, commit-limit failure, abort after upload, abort while overwriting, and verifyStreamWasAborted().


## Control Flow
Valid two-part uploads should complete. Larger writes and committer uploads are expected to raise PathIOException and leave no destination. Abort tests write multipart data then call stream.abort(), assert no object materializes or previous contents survive, and verify stream/filesystem IOStatistics counters.


## State and Persistence Behavior
Persistent S3 state is the target object path, which must either not exist after failed/aborted uploads or retain original contents after overwrite abort. Temporary local commit files are created for CommitOperations upload tests.


## Dependencies and Integration Points
Depends on S3A commit operations, FSDataOutputStream Abortable, ExtraAssertions abort helpers, S3AInstrumentation counters, IOStatistics assertions, and multipart support assumptions.


## Risks and Test Signals
Risks include leaked MPU parts or overwriting existing data after abort. Test signals include PathIOException interception, path absence/content verification, committer abort counters, and stream abort/multipart abort statistics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AMultipartUploadSizeLimits.java -->
