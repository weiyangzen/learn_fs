<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java

## Purpose

`CountInvocationsProvider` is a deliberately failing AWS credentials provider used by delegation-token tests to prove that delegated-token credential chains override ordinary configured providers. If it is invoked, it increments counters and throws, making unexpected fallback visible.

## Important APIs, Types, and Functions

- Implements AWS SDK v2 `AwsCredentialsProvider`.
- `NAME` exposes the provider class name for configuration strings.
- Static `COUNTER` tracks global invocations across all provider instances.
- `instanceCounter` tracks invocations per instance.
- `resolveCredentials()` increments both counters, logs a message, and throws `CredentialInitializationException`.
- `getInvocationCount()` and `getInstanceCounter()` expose counters for assertions.

## Control Flow and State

Tests bind this provider into `fs.s3a.aws.credentials.provider`, then execute a delegated S3A operation. A successful delegation path should never call `resolveCredentials()`, leaving the global counter unchanged. If S3A incorrectly falls back to normal credentials, the provider throws and the test fails.

## State and Persistence Behavior

State is purely in-memory through `AtomicLong` counters. The static counter persists across provider instances in the same JVM and can therefore be used to compare before/after counts in a test.

## Dependencies and Integration Points

It integrates with S3A's AWS credentials provider loading and AWS SDK v2 credential interface. It is referenced by `ITestSessionDelegationInFilesystem` through `CountInvocationsProvider.NAME`.

## Risks and Edge Cases

Because the global counter is static and not reset in this class, tests should compare deltas rather than assume zero. The provider never returns credentials by design.

## Test Signals

The signal is negative: an unchanged invocation count proves the delegated-token provider chain was selected; a thrown `CredentialInitializationException` or increased count points to incorrect credential fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/CountInvocationsProvider.java -->
