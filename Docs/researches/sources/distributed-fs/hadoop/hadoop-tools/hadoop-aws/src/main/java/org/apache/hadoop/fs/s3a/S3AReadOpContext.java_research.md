# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3AReadOpContext.java

## Purpose
`S3AReadOpContext` extends `S3AOpContext` with all read/open-specific configuration needed to create and operate an S3A input stream.

## Important APIs, Types, and Functions
It exposes builder-style setters `withInputPolicy()`, `withChangeDetectionPolicy()`, `withReadahead()`, `withAuditSpan()`, and `withAsyncDrainThreshold()`, validation via `build()`, and getters for path, read invoker, input policy, change detection, readahead, audit span, async drain threshold, `VectoredIOContext`, `IOStatisticsAggregator`, and `ExecutorServiceFuturePool`.

## Control Flow and State
The constructor stores immutable references for path, vectored IO, statistics aggregation, and future pool. Callers then set required mutable fields and call `build()`, which verifies required policies/spans and non-negative numeric thresholds. The resulting object is passed to read stream creation and async/vector read code.

## State and Persistence Behavior
The context is per-read and in-memory. It is mutable until build but not made immutable afterward; callers are expected to treat it as configured state. It holds references to audit and async execution state but persists no data.

## Dependencies and Integration Points
Dependencies include `S3AInputPolicy`, `ChangeDetectionPolicy`, `AuditSpan`, `VectoredIOContext`, `IOStatisticsAggregator`, `ExecutorServiceFuturePool`, `Invoker`, `FileStatus`, and `S3AStatisticsContext`. It integrates with `S3AInputStream` construction, vectored reads, async prefetch/drain behavior, and change tracking.

## Risks and Test Signals
Risks include forgotten `build()` validation, mutation after validation, null future/aggregator handling, negative readahead/drain thresholds, and losing audit span context for later reads. Tests should verify required field checks, threshold validation, propagation to stream constructors, and correct vectored/async settings in read behavior.
