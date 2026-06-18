<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java


## Purpose
Minimal WriteOperationHelper callback implementation that delegates actual multipart calls to a supplied S3Client.


## Important APIs, Types, and Functions
Defines a Supplier<S3Client> field, constructor, completeMultipartUpload(), and uploadPart().


## Control Flow
On each callback it resolves the S3Client supplier and invokes completeMultipartUpload or uploadPart. A null supplier result intentionally causes NullPointerException for tests expecting failure.


## State and Persistence Behavior
State is only the supplier reference. S3 service state is affected only when delegated client calls are real rather than mocked.


## Dependencies and Integration Points
Depends on WriteOperationHelper.WriteOperationHelperCallbacks, AWS SDK S3Client, multipart request/response types, RequestBody, and DurationTrackerFactory.


## Risks and Test Signals
Risks are on-demand supplier side effects and missing duration tracking in uploadPart. Test signal is controlled delegation into mocked or instrumented S3 clients.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/test/MinimalWriteOperationHelperCallbacks.java -->
