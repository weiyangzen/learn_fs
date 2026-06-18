<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java -->
# sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java

## Purpose

`ILoadTestSessionCredentials` is a load/scale test that creates many S3A delegation tokens backed by AWS STS session credentials to observe latency and throttling behavior. It is intentionally high impact and documented as potentially disruptive to a shared AWS account.

## Important APIs, Types, and Functions

- `createScaleConfiguration()` enables the configured delegation-token binding, increases S3A connection count to at least `THREADS`, and disables S3A error retries.
- `getDelegationBinding()` defaults to `DELEGATION_TOKEN_SESSION_BINDING`.
- `setup()` assumes session tests are enabled, verifies canonical service name, and creates a local data directory.
- `testCreate10Tokens()` fetches 10 tokens and logs CSV content.
- `testCreateManyTokens()` fetches 50,000 tokens.
- `fetchTokens(int, File)` submits token-fetch callables to a 100-thread executor and records outcomes.
- Nested `Outcome` records id, wall-clock start, nano timer, and optional exception, then writes rows and schema through `Csvout`.

## Control Flow and State

The test builds a fixed thread pool and `ExecutorCompletionService`. For each token request it submits a task that calls `fileSystem.getDelegationToken("Count ")`, captures any `IOException`, and returns an `Outcome`. The main thread consumes completed outcomes, writes each CSV row, and aggregates three `NanoTimerStats` groups: overall, successful, and throttled.

## State and Persistence Behavior

It writes CSV timing files named `session-<tokens>.csv` under `GenericTestUtils.getTestDir("kerberos")`. The executor is a field and is not explicitly shut down in the file, relying on test lifecycle/JVM handling. S3A remote state is limited to STS calls and token creation, not object writes.

## Dependencies and Integration Points

The test uses `S3AScaleTestBase`, `S3AFileSystem.getDelegationToken()`, delegation constants, Hadoop executor utilities, Guava `ThreadFactoryBuilder`, `NanoTimerStats`, Apache Commons IO for reading the short CSV, and live AWS STS behavior.

## Risks and Edge Cases

The documented risk is AWS STS throttling that can affect other users in the same AWS account. Disabling retries makes throttling visible but also makes the workload less resilient. CSV writing is simple and only externally quotes the exception message. Very large runs may be slow and generate large output files.

## Test Signals

Signals are per-request CSV rows containing success flag, start/end/duration, and error message; logged aggregate timer stats; throttled-event counts; and effective operations per second.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-tools/hadoop-aws/src/test/java/org/apache/hadoop/fs/s3a/auth/delegation/ILoadTestSessionCredentials.java -->
