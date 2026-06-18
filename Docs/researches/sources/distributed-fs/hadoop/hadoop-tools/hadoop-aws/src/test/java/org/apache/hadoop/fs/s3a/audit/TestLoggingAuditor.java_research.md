# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/TestLoggingAuditor.java

## Purpose

`TestLoggingAuditor.java` validates logging-auditor span behavior, out-of-span rejection, permitted out-of-span request types, transfer listener span propagation, span IDs, and HTTP response statistic extraction.

## Important APIs, Types, and Functions

It uses `LoggingAuditor`, `AuditManagerS3A`, AWS SDK request models such as `UploadPartCopyRequest`, `GetBucketLocationRequest`, and `CompleteMultipartUploadRequest`, `TransferListener`, and failure contexts created with `DefaultFailedExecutionContext`.

## Control Flow

The main span test creates a span, successfully issues a HEAD, deactivates/close spans and expects unaudited HEAD failures, then reactivates spans to allow requests again. Transfer tests create listeners inside/outside spans and verify callback activation. Error tests feed synthetic 400/500 HTTP responses into span failure handling.

## State and Persistence Behavior

Active span state is thread-local/manager-local. IOStatistics counters record audit request execution/failure and HTTP response class counters.

## Dependencies and Integration Points

The suite covers logging auditor, AWS SDK execution failure handling, transfer manager listener integration, and the audit manager's allowlist for background transfer requests.

## Risks and Edge Cases

Transfer-manager background threads require selected operations outside normal spans. Overly strict rejection would break uploads/copies; overly loose handling would hide unaudited user requests.

## Test Signals

Signals include audit execution/failure counter deltas, successful allowlisted request callbacks outside spans, active span restoration through transfer listener, distinct span IDs, and `HTTP_RESPONSE_400`/`HTTP_RESPONSE_500` counter increments.
