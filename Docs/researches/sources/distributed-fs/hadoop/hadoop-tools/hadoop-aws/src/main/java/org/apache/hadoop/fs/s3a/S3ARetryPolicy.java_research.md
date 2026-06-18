# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/main/java/org/apache/hadoop/fs/s3a/S3ARetryPolicy.java

## Purpose
`S3ARetryPolicy` defines how S3A retries translated Hadoop/AWS failures. It separates normal IO retry limits, throttling retry limits, connectivity failures, non-idempotent operation filtering, and fail-fast exceptions.

## Important APIs, Types, and Functions
The primary API is `shouldRetry(Exception, int, int, boolean)`. Constructor-created policies include `baseExponentialRetry`, `retryIdempotentCalls`, `throttlePolicy`, `connectivityFailure`, `retryAwsClientExceptions`, and `http5xxRetryPolicy`. Extension hooks are `createThrottleRetryPolicy()` and `createExceptionMap()`. Internal filters are `IdempotencyRetryFilter`, `FailNonIOEs`, and unused-ready `RetryFromAWSClientExceptionPolicy`.

## Control Flow and State
Construction reads retry counts/intervals from configuration, builds exponential policies, creates a class-exact exception map, and wraps it in `retryByException()`. `shouldRetry()` translates raw AWS SDK exceptions through `S3AUtils.translateException()` before policy lookup, logs the probe, then delegates to the composed policy.

## State and Persistence Behavior
State is immutable after construction and backed by configuration-derived values. It persists no retry history itself; Hadoop retry callers pass retry counters on each probe.

## Dependencies and Integration Points
Dependencies include Hadoop `RetryPolicy`, S3A exception classes, `S3AUtils`, AWS SDK `SdkException`, and configuration constants such as `RETRY_LIMIT`, `RETRY_INTERVAL`, `RETRY_THROTTLE_LIMIT`, and `RETRY_HTTP_5XX_ERRORS`. It is used by `Invoker` and store/filesystem operations annotated with retry semantics.

## Risks and Test Signals
Risks include exact-class mapping missing subclasses, unsafe retries for non-idempotent calls, under/over-retrying 5xx or throttled failures, and behavior changes when AWS SDK exception translation changes. Tests should cover translated status codes, throttling retry even for non-idempotent calls, fail-fast auth/not-found/unsupported cases, connectivity retries, HTTP 5xx configuration, and raw `SdkException` handling.
