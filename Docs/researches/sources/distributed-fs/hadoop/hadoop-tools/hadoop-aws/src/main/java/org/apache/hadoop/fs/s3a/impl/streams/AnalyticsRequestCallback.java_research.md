# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/streams/AnalyticsRequestCallback.java

## Purpose
`AnalyticsRequestCallback` adapts AWS Analytics Accelerator request callbacks into S3A input stream statistics updates.

## Important APIs and Types
It implements AAL `RequestCallback` and holds `S3AInputStreamStatistics`. Methods map GET, HEAD, block prefetch, footer parse failure, vectored read, and cache-hit callbacks to statistics methods.

## Control Flow
The analytics stream passes an instance into `OpenStreamInformation`; AAL invokes callbacks during read operations and prefetch. Each callback immediately updates S3A statistics.

## State and Persistence
It stores a statistics reference and mutates in-memory metrics. No persistence.

## Dependencies and Integration Points
It depends on `software.amazon.s3.analyticsaccelerator.util.RequestCallback` and S3A input stream statistics. It is created by `AnalyticsStream`.

## Risks and Edge Cases
Statistics must be non-null; no null checks are performed. Callback frequency may be high, so stats methods should be lightweight.

## Test Signals
Tests should assert each AAL callback increments the intended S3A statistic, including prefetch byte calculation `end - start + 1`.
