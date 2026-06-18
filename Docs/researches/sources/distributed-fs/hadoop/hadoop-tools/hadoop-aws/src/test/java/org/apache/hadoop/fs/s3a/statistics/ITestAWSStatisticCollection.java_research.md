<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java


## Purpose
Cost/statistics integration test that verifies AWS SDK request metrics are wired into S3A IO statistics.


## Important APIs, Types, and Functions
ITestAWSStatisticCollection overrides createConfiguration() to disable S3 Express create sessions and set create performance flags, and testSDKMetricsCostOfGetFileStatusOnFile().


## Control Flow
The test creates a simple file via AbstractS3ACostTest.file(), calls getFileStatus(), and verifies STORE_IO_REQUEST increased by one using the cost-test metric harness.


## State and Persistence Behavior
Persistent state is a single test file; statistics state is captured around the operation by verifyMetrics().


## Dependencies and Integration Points
Depends on AbstractS3ACostTest, S3AFileSystem, S3A performance flags, S3EXPRESS_CREATE_SESSION, and Statistic.STORE_IO_REQUEST.


## Risks and Test Signals
Risk is metric name/wiring drift between AWS SDK and S3A counters. The signal is intentionally narrow: one getFileStatus should produce one SDK IO request.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAWSStatisticCollection.java -->
