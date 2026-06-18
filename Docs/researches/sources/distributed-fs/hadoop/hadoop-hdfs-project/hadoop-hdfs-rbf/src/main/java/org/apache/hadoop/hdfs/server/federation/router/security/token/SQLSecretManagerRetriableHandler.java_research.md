# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLSecretManagerRetriableHandler.java

## Purpose
This file defines the retry abstraction used by SQL token persistence and its `RetryProxy`-based implementation.

## Important APIs, Types, And Functions
`SQLSecretManagerRetriableHandler` exposes `execute(SQLCommandVoid)` and `<T> execute(SQLCommand<T>)`. Nested functional interfaces represent SQL commands. Package-private `SQLSecretManagerRetriableHandlerImpl` defines `MAX_RETRIES`, `RETRY_SLEEP_TIME_MS`, `getInstance`, execution methods, and `SQLSecretManagerRetriableException`.

## Control Flow
`getInstance` builds an exponential-backoff retry policy for `SQLSecretManagerRetriableException` and a try-once policy for all other exceptions, then wraps the implementation in a Hadoop `RetryProxy`. Execution methods run the command and convert any `SQLException` into the retryable subclass.

## State, Persistence, And Dependencies
No persistent state exists. Runtime state is the proxy and retry policy. Dependencies include Hadoop retry utilities, `Configuration`, and SQL token-manager config prefixes.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` wraps every JDBC persistence operation with this handler.

## Risks
All SQLExceptions are treated as retryable at the implementation boundary, so permanent syntax/schema/auth errors may be retried until the configured budget is exhausted. Defaults allow zero retries. Because the implementation class is package-private, tests in other packages need to use the interface or same package.

## Test Signals
Tests should verify zero-retry default, configured retry counts and sleep, retry on wrapped SQLExceptions, no retry for non-SQL runtime exceptions, return values from generic commands, and logging of failed SQL commands.
