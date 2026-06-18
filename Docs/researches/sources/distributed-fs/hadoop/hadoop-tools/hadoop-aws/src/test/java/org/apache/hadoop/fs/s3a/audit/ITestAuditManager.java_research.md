# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/ITestAuditManager.java

## Purpose

`ITestAuditManager.java` verifies audit request execution in a real S3A filesystem, including rejection of out-of-span S3 calls and loading of extra AWS SDK execution interceptors.

## Important APIs, Types, and Functions

The test enables the logging auditor, sets `AUDIT_EXECUTION_INTERCEPTORS` to `SimpleAWSExecutionInterceptor.CLASS`, and intentionally sets invalid legacy request handlers. `testInvokeOutOfSpanRejected()` exercises `WriteOperationHelper.listMultipartUploads()`. `testExecutionInterceptorBinding()` executes `fs.listStatus("/")`.

## Control Flow

The first test closes a span so the writer holds an invalid span, expects an `AccessDeniedException` wrapping `AuditFailureException`, verifies audit counters increased, then permits out-of-band operations and retries. The second records interceptor invocation count, performs a listing, and asserts the custom interceptor ran with the filesystem configuration.

## State and Persistence Behavior

Audit flags can be changed at runtime through `setAuditFlags()`. Counter state lives in filesystem IOStatistics. `SimpleAWSExecutionInterceptor` records static invocation/config state.

## Dependencies and Integration Points

It integrates S3A write helpers, logging audit manager, AWS SDK interceptor extension loading, and IOStatistics counters.

## Risks and Edge Cases

The test is sensitive to configurations that disable out-of-span rejection, so it uses an assumption guard. Invalid request-handler config should not prevent execution-interceptor loading.

## Test Signals

Signals are increasing `AUDIT_REQUEST_EXECUTION` and `AUDIT_FAILURE` counters, an access-denied exception with unaudited-operation text, and custom interceptor invocation/config capture.
