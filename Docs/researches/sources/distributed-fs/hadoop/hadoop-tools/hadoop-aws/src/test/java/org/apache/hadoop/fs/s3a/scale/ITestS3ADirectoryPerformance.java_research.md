<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java -->

# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java


## Purpose
Scale/performance coverage for S3A directory listing, recursive scans, content summaries, paged listings, and repeated getFileStatus calls.


## Important APIs, Types, and Functions
ITestS3ADirectoryPerformance exposes testListOperations(), testMultiPagesListingPerformanceAndCorrectness(), getConfigurationWithConfiguredBatchSize(), sleep(), stat timing tests, and timeToStatPath(). It uses MetricDiff counters and WriteOperationHelper for direct PUTs.


## Control Flow
The first test creates a synthetic directory tree and compares explicit treewalk, listFiles(recursive=true), and getContentSummary results while validating expected object-list request counts. The paged-listing test uploads 1000 zero-byte objects in parallel, exercises listFiles/listStatus/listStatusIterator/listLocatedStatus with MAX_PAGING_KEYS=10, and checks continuation counters. Stat tests repeat getFileStatus over file, empty/non-empty directory, and root paths.


## State and Persistence Behavior
Persistent S3 state consists of generated directories/files under method paths and is deleted in finally blocks. Per-iterator IOStatistics are inspected after traversal; filesystem statistics are logged before closing the uncached FS.


## Dependencies and Integration Points
Depends on S3A internals including RequestFactory, WriteOperationHelper, S3ADataBlocks, audit spans, RemoteIterators, IOStatistics retrieval, object list/continue counters, and ContractTestUtils tree builders.


## Risks and Test Signals
Expensive and latency-sensitive due to 1000 PUTs and intentional per-file sleeps. It detects listing pagination bugs, incorrect directory marker/content-summary semantics, missing iterator statistics, and inefficient extra LIST/HEAD requests.

<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/scale/ITestS3ADirectoryPerformance.java -->
