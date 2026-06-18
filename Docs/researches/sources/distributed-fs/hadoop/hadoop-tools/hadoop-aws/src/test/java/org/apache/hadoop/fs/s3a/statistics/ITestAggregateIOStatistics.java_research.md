<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java


## Purpose
Integration test for serializing aggregate IOStatistics snapshots to local disk and to S3.


## Important APIs, Types, and Functions
ITestAggregateIOStatistics defines testSaveStatisticsLocal(), testSaveStatisticsS3(), createOutputDir(), and outputFilename(). It uses IOStatisticsSnapshot.serializer().


## Control Flow
Local test aggregates filesystem statistics, writes JSON under test.build.dir/classname with a timestamped filename, reloads it, and logs the deserialized string. S3 test writes the same snapshot to methodPath and reloads from the filesystem.


## State and Persistence Behavior
State persists as a local JSON file and an S3 object. It also reads/writes the static FILESYSTEM_IOSTATS aggregate inherited from the base test class.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, JsonSerialization, IOStatisticsSnapshot, local filesystem, and S3A filesystem serializer overloads.


## Risks and Test Signals
Risks include timestamp collision only at extreme speed, permissions on target build dir, and serializer compatibility. Signals validate round-trip persistence in both local and S3-backed stores.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestAggregateIOStatistics.java -->
