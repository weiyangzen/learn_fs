<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml


## Purpose
Contract-test capability declaration for S3A filesystem behavior.


## Important APIs, Types, and Functions
The XML defines fs.contract.* properties covering root tests, random seek count, blobstore identity, visibility delay, case sensitivity, rename semantics, unsupported append/concat/atomic operations, seek/unbuffer/vector IO, multipart uploader support, permissions, and create-under-file behavior.


## Control Flow
Contract tests load these properties to decide expected behavior and which assertions to run. Duplicate rename-overwrites-dest entries both set false.


## State and Persistence Behavior
State is configuration data only; it does not execute code or persist runtime state. It shapes downstream contract-test expectations.


## Dependencies and Integration Points
Depends on Hadoop contract test framework property names and S3A's documented blobstore semantics.


## Risks and Test Signals
Risks are stale properties causing false contract failures or masking regressions. Signals encode S3A's non-POSIX semantics, especially non-atomic rename/delete and delayed create visibility.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/resources/contract/s3a.xml -->
