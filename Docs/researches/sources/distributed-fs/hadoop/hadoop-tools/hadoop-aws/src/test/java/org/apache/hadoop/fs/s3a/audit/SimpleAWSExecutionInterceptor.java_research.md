# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/audit/SimpleAWSExecutionInterceptor.java

## Purpose

`SimpleAWSExecutionInterceptor.java` is a test AWS SDK v2 `ExecutionInterceptor` used to verify dynamic interceptor loading and configuration injection through S3A auditing setup.

## Important APIs, Types, and Functions

The class extends `Configured`, implements `ExecutionInterceptor`, exposes class name `CLASS`, keeps static `AtomicLong INVOCATIONS`, and static `Configuration staticConf`. `beforeExecution()` increments the counter and captures `getConf()`.

## Control Flow

When an AWS SDK request reaches `beforeExecution()`, the interceptor records that it was invoked and stores the configured Hadoop `Configuration`.

## State and Persistence Behavior

State is process-static and persists across test methods unless explicitly accounted for. Tests compare deltas rather than assuming zero.

## Dependencies and Integration Points

It integrates with `AUDIT_EXECUTION_INTERCEPTORS`, `AuditManagerS3A.createExecutionInterceptors()`, and real S3 request execution in audit manager tests.

## Risks and Edge Cases

Static state can leak across tests, so assertions must use base counts. It does not validate request contents; it only proves invocation and configuration binding.

## Test Signals

Signals are an increased invocation count and `staticConf` identity matching the filesystem configuration.
