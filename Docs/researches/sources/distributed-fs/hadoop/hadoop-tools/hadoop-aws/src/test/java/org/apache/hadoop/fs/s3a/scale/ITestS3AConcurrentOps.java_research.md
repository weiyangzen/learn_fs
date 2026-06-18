<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java


## Purpose
Scale test for concurrent rename/copy/delete operations sharing one S3AFileSystem and for transfer-thread pool cooldown after active work.


## Important APIs, Types, and Functions
ITestS3AConcurrentOps, createScaleConfiguration(), setup(), getNormalFileSystem(), parallelRenames(), testParallelRename(), and testThreadPoolCoolDown(). It tunes MULTIPART_SIZE to the minimum and uses MAX_THREADS/MAX_TOTAL_TASKS to force tiny executor resources.


## Control Flow
The test creates 10 source files through an auxiliary FS, each with repeated 1 MiB blocks, then submits concurrent fs.rename() tasks on another S3AFileSystem. It waits for all futures, validates target existence and source absence, and separately counts live s3a-transfer threads before and after keepalive expiry.


## State and Persistence Behavior
State lives in S3 paths under methodPath(); teardown deletes the test root through the auxiliary FS. The tiny-thread-pool variant intentionally stresses bounded task queues and transfer pools to catch deadlock-prone scheduling.


## Dependencies and Integration Points
Depends on S3AFileSystem, SubjectInheritingThread, ContractTestUtils datasets/timers, executor services, multipart copy support, and default transfer keepalive configuration.


## Risks and Test Signals
The test is sensitive to S3 latency, configured multipart support, and JVM thread naming. It is a strong signal for deadlocks, copy executor starvation, and transfer-pool resource leaks after rename workloads.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AConcurrentOps.java -->
