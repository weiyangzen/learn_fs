# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/TestInvoker.java

## Purpose

Unit test suite for `Invoker`, `S3ARetryPolicy`, and S3A exception translation/retry behavior. It focuses on 5xx handling, throttling, connectivity failures, shaded timeout class matching, EOF-like SDK errors, non-idempotent operations, and quiet evaluation helpers.

## Important APIs, Types, and Functions

Key APIs are `Invoker.retry()`, `Invoker.quietlyEval()`, `S3ARetryPolicy.shouldRetry()`, `S3AUtils.translateException()`, `extractException()`, and AWS SDK exception builders. Constants configure fast retry intervals, active retry limits, and retrying HTTP 5xx errors.

## Control Flow

Tests translate S3 status codes to specific S3A IO exceptions, assert retry decisions for 500/501/503/504 and generic 5xx responses under enabled/disabled policies, repeatedly retry operations that fail until a counter threshold, and verify non-idempotent bad requests are not retried. Timeout tests wrap local, Hadoop, Apache HTTP, execution, and completion exceptions to ensure extraction and classname-based matching. Quiet helpers are tested for void and return-value behavior.

## State, Dependencies, and Integration Points

State includes retry count, retry policies built from `Configuration`, and synthetic AWS exceptions. It integrates Hadoop retry policy contracts, AWS SDK v2 exception hierarchy, shaded Apache HTTP classes, and S3A's IO exception taxonomy.

## Risks and Test Signals

These tests encode precise retry policy semantics. They are sensitive to AWS SDK exception text/class changes and configuration defaults for 5xx retries. Strong signals include exact translated exception classes, retry/fail decisions, retry counters, and no retry of NPEs or interrupted IO.
