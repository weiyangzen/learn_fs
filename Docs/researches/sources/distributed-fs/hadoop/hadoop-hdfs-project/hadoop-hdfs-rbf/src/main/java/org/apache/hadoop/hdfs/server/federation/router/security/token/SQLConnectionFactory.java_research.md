# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLConnectionFactory.java

## Purpose
`SQLConnectionFactory` defines the connection-provider contract for SQL-backed router delegation token persistence.

## Important APIs, Types, And Functions
It declares config key constants for URL, username, password, and driver. Required methods are `Connection getConnection()` and `shutdown()`. The default `getConnection(boolean autocommit)` sets autocommit on a new connection.

## Control Flow
Implementations return a JDBC connection. The default autocommit overload obtains a connection and mutates its autocommit mode before returning it.

## State, Persistence, And Dependencies
The interface has no state. Persistence is external SQL database state. It depends on JDBC and Hadoop SQL delegation token configuration prefixes.

## Integration Points
`HikariDataSourceConnectionFactory`, `DistributedSQLCounter`, and `SQLDelegationTokenSecretManagerImpl` use this contract.

## Risks
If `setAutoCommit` fails, callers receive an exception but the newly opened connection may need implementation-level cleanup. Implementations must define shutdown semantics carefully to avoid leaking pools.

## Test Signals
Tests should cover factory implementations, autocommit true/false behavior, shutdown idempotence, and exception handling when connection setup fails.
