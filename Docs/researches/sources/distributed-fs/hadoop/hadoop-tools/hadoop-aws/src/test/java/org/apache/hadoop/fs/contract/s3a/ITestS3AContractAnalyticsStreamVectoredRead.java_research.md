# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/contract/s3a/ITestS3AContractAnalyticsStreamVectoredRead.java

Purpose: S3A contract test proving Hadoop's base `PositionedReadable.readVectored()` behavior works when S3A uses the Analytics Accelerator stream.

Important APIs/types/functions: extends `AbstractContractVectoredReadTest`, parameterized by buffer type. `createConfiguration()` disables filesystem caching, removes Analytics Accelerator bucket overrides, configures coalescing/read-buffer/cache options, enables AAL, and skips unsupported encryption modes. Overrides `testNegativeOffsetRange()` to expect `IllegalArgumentException` and skips `testNullReleaseOperation()` for a known AAL null-release gap. Adds `testReadVectoredWithAALStatsCollection()`.

Control flow: the stats test builds four ranges, reads them through `FSDataInputStream.readVectored()`, validates data, then verifies AAL stream-open, vectored operation, incoming/combined range, HTTP GET, and cache-hit counters. It rereads the same ranges to assert no extra GETs.

State and persistence: creates S3 test objects inherited from the contract suite; modifies only per-test configuration.

Dependencies and integration: depends on AAL configuration keys under `ANALYTICS_ACCELERATOR_CONFIGURATION_PREFIX`, S3A test utilities, contract vector helpers, and IOStatistics counters.

Risks: sensitive to AAL implementation details, cache timeout, coalescing tolerance, and encryption/eTag behavior. Counter values can be brittle across AAL upgrades.

Test signals: integration and parameterized contract coverage for analytics-stream vectored read correctness and statistics.
