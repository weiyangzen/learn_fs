<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java


## Purpose
Integration test that filesystem-level bytesRead aggregates reads from multiple S3A input streams.


## Important APIs, Types, and Functions
ITestS3AFileSystemStatistic defines constants ONE_KB/TWO_KB and testBytesReadWithStream().


## Control Flow
The test writes 1 KiB, asserts the output stream counted STREAM_WRITE_BYTES, reads the file fully through two separate input streams, then asserts FileSystem.Statistics.getBytesRead() equals 2 KiB.


## State and Persistence Behavior
Persistent state is one S3 test file. Statistics state is the S3AFileSystem instance's shared FileSystem.Statistics object.


## Dependencies and Integration Points
Depends on AbstractS3ATestBase, FSDataInputStream/OutputStream, S3AFileSystem, IOStatisticAssertions, and StreamStatisticNames.


## Risks and Test Signals
Risks are global statistics contamination if filesystem reuse changes and exact byte-count assumptions if reads overfetch. Signal verifies user-visible FS statistics, not only per-stream IOStatistics.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/statistics/ITestS3AFileSystemStatistic.java -->
