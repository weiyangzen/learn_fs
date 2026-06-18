# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AAnalyticsAcceleratorStreamReading.java

Purpose: integration suite for S3A's Analytics Accelerator input stream, including connector framework wiring, prefetch/cache behavior, parquet handling, invalid configuration, and request statistics.

Important APIs/types/functions: extends `AbstractS3ATestBase`; `createConfiguration()` enables AAL. Setup skips CSE and resolves an external test file. Tests cover whole-file policy, sequential prefetching, malformed parquet footer, multi-row-group parquet, invalid AAL config, random-seek cache behavior, and sequential streams sharing cache.

Control flow: tests open files with `openFile()` policies or normal `open()`, inspect wrapped `ObjectInputStream`, and assert stream type/policy plus IOStatistics counters for GET/HEAD, audit requests, bytes read, prefetched bytes, cache hits, and parquet footer failures. Some tests copy local parquet resources into S3 before reading.

State and persistence: reads public external data and writes local test resources or generated datasets to the test bucket. AAL cache behavior spans streams/factory lifetime until FS close.

Dependencies and integration: AWS Analytics Accelerator library, S3A connector stream framework, IOStatistics, audit statistics, local parquet resources, and public dataset utilities.

Risks: exact GET/prefetch/cache counters are highly sensitive to AAL version, file size, cache timeout, and public dataset contents. Tests skip CSE due to incompatibility.

Test signals: broad integration coverage for AAL stream selection, caching, prefetching, parquet optimizations, and stats propagation.
