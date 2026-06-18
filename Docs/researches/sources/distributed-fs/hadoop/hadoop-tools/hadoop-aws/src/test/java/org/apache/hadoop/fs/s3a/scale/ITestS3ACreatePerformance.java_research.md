<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java


## Purpose
Single-thread create() scale/performance test for deeply nested S3A paths.


## Important APIs, Types, and Functions
ITestS3ACreatePerformance with setup(), testDeepSequentialCreate(), and getPathIteration(). It uses S3AScaleTestBase operation counts and a fixed PATH_DEPTH of 10.


## Control Flow
Before each run it records the base path and depth, then creates getOperationCount() one-byte files below uniquely generated nested directories. A NanoTimer reports total and per-create timing.


## State and Persistence Behavior
The test persists many small objects under getTestPath(); each object name embeds the iteration number to avoid overwrite collisions. No custom cleanup state is held beyond basePath/basePathDepth.


## Dependencies and Integration Points
Depends on S3AFileSystem.create(), Path depth semantics, ContractTestUtils.NanoTimer, and scale-test configuration keys.


## Risks and Test Signals
Risks are cost and runtime from many small PUTs and directory marker side effects. Test signals are performance timing plus assertion that the requested path depth is actually deeper than the configured base path.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ACreatePerformance.java -->
