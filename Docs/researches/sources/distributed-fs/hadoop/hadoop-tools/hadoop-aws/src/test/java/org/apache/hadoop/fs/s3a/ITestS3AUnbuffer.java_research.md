# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/ITestS3AUnbuffer.java

## Purpose

Integration coverage for `CanUnbuffer.unbuffer()` on `S3AInputStream`. It writes a small real S3A test object, opens it through `FSDataInputStream`, verifies the wrapped stream is an `S3AInputStream`, and proves that `unbuffer()` closes the underlying object stream while preserving readable stream state.

## Important APIs, Types, and Functions

Key APIs are `FSDataInputStream.open/read/unbuffer/getIOStatistics`, `StreamCapabilities.UNBUFFER`, `S3AInputStream.isObjectStreamOpen()`, `S3AInputStreamStatistics`, `IOStatisticsSnapshot`, and `S3ATestUtils.MetricDiff`. The helpers `isObjectStreamOpen()`, `skipIfCannotUnbuffer()`, and `readAndAssertBytesRead()` keep assertions focused on stream support and exact byte counts.

## Control Flow

`setup()` creates `ITestS3AUnbuffer` with 16 bytes. `testUnbuffer()` reads 8 bytes, snapshots IO statistics, calls `unbuffer()`, then checks `STREAM_READ_UNBUFFERED`, `STREAM_READ_BYTES`, and HTTP GET counts without a second GET. `testUnbufferStreamStatistics()` performs two read/unbuffer cycles, compares filesystem metric deltas for bytes read and close-drained bytes, closes the stream, and asserts close does not double-count.

## State, Dependencies, and Integration Points

State is held in the S3 object, the live wrapped AWS object stream, per-stream IO statistics, and filesystem instrumentation counters. It depends on `AbstractS3ATestBase`, contract dataset helpers, S3A stream capabilities, and Hadoop IOStatistics.

## Risks and Test Signals

The suite is sensitive to alternative stream implementations and skips if unbuffer capability is absent. It catches regressions where unbuffer fails to close the HTTP stream, loses IO statistics, double-counts close bytes, or leaves filesystem counters inconsistent after repeated unbuffer calls.
