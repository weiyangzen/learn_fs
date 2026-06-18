<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java

## Purpose

`ILoadTestRoleCredentials` reuses the session-credential STS load test with the role delegation-token binding. It measures the cost and throttling behavior of assume-role credential creation relative to plain session token creation.

## Important APIs, Types, and Functions

- Extends `ILoadTestSessionCredentials`.
- Annotated with `@LoadTest` and `@ScaleTest`.
- `getDelegationBinding()` returns `DELEGATION_TOKEN_ROLE_BINDING`.
- `getFilePrefix()` returns `role`, causing CSV files to use the role prefix.

## Control Flow and State

All execution flow is inherited from `ILoadTestSessionCredentials`: setup configures delegation tokens and an executor, tests call `fetchTokens()`, many concurrent calls invoke `fileSystem.getDelegationToken()`, and outcomes are written to CSV. This subclass changes only the binding and output filename prefix.

## State and Persistence Behavior

The inherited load test writes timing CSV files under the test data directory. It uses the same executor, completion service, and outcome aggregation as the session variant.

## Dependencies and Integration Points

It depends on role-token binding configuration and, in practice, on S3A test configuration that can assume a configured role. It is part of the high-cost load/scale test path rather than ordinary unit test execution.

## Risks and Edge Cases

Because role credentials require STS AssumeRole, this test can trigger AWS STS throttling and may affect a shared AWS account. It inherits the load-test warning profile from the parent.

## Test Signals

Signals are CSV rows and logged summary stats for total requests, successful requests, throttled requests, duration distributions, and effective operations per second.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestRoleCredentials.java -->
