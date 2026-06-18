<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java


## Purpose
Comprehensive scale/performance test for classic S3A input stream read policies, seeking, readahead, decompression, random IO, and stream statistics.


## Important APIs, Types, and Functions
ITestS3AInputStreamPerformance defines openFS(), cleanup(), openTestFile()/openDataFile(), assertOpenOperationCount(), testTimeToOpenAndReadWholeFileBlocks(), bandwidth(), lazy seek/readahead tests, decompression, executeSeekReadSequence(), executeRandomIO(), getS3aStream(), and testRandomReadOverBuffer().


## Control Flow
Setup binds a new S3AFileSystem to a configured public gzipped test object, using classic streams and disabled prefetch. Tests read full files in 1 MiB blocks, verify lazy seeks do not open streams, reject negative readahead, exercise normal/sequential/random policies, decompress through LineReader, and perform positioned reads spanning readahead ranges. IOStatistics are logged and aggregated after each test.


## State and Persistence Behavior
State includes the external test object status, a per-test FSDataInputStream, S3AInputStreamStatistics, aggregate static IOStatisticsSnapshot, and one local test object for buffer-boundary reads. No production state is persisted except temporary test paths.


## Dependencies and Integration Points
Depends on PublicDatasetTestUtils, S3AInputStream internals, FutureDataInputStreamBuilder options, CompressionCodecFactory, LineReader, stream statistic names, IOStatistics assertions, and public S3 datasets.


## Risks and Test Signals
Risks are external dataset availability, client-side encryption incompatibility, network variability, and exact statistics changes. Strong signals include open-operation counts, abort/policy-change counters, HTTP GET timing samples, and byte-for-byte buffer checks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3AInputStreamPerformance.java -->
