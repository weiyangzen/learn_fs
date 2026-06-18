<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java

## Purpose

`BulkDeleteRetryHandler` records statistics and throttle logging when bulk delete operations are retried.

## Important APIs, Types, and Functions

It exposes `bulkDeleteRetried(DeleteObjectsRequest, Exception)`, protected `incrementStatistic()` overloads, and private helpers `onDeleteThrottled()` and `isSymptomOfBrokenConnection()`.

## Control Flow

On retry, throttling exceptions update throttled counters and quantiles by the number of keys in the request. XML parse failures wrapped as `AWSClientIOException`/`SdkClientException` are treated as broken-connection symptoms and counted as throttling. Other failures increment ignored-error statistics.

## State and Persistence Behavior

The handler stores references to the context instrumentation and storage statistics. It does not persist retry history.

## Dependencies and Integration Points

It depends on S3A statistics, S3A throttle exception predicates, AWS `DeleteObjectsRequest`, and the dedicated throttle logger.

## Risks and Edge Cases

`onDeleteThrottled()` assumes the request has at least one key because it logs first and last keys. Broken-connection detection relies on exception type and message text containing `Failed to parse XML document`.

## Test Signals

Exercise throttled exceptions, XML parse broken-connection symptoms, generic exceptions, statistic increments by key count, quantile updates, and empty-request behavior if reachable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/impl/BulkDeleteRetryHandler.java -->
