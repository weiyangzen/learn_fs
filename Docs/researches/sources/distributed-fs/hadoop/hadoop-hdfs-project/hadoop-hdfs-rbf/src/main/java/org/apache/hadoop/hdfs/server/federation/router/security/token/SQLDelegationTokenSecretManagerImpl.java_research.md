# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/SQLDelegationTokenSecretManagerImpl.java

## Purpose
`SQLDelegationTokenSecretManagerImpl` persists router delegation tokens and delegation keys in SQL tables and coordinates distributed sequence allocation.

## Important APIs, Types, And Functions
It extends `SQLDelegationTokenSecretManager<AbstractDelegationTokenIdentifier>`. Overrides include `createIdentifier`, `stopThreads`, token insert/update/delete/select/stale-select methods, delegation-key insert/update/delete/select methods, and sequence/key counter select/update/increment methods. It owns a `SQLConnectionFactory`, `DistributedSQLCounter` instances, and a `SQLSecretManagerRetriableHandler`.

## Control Flow
Construction creates the connection factory and retry handler, initializes two distributed counters, starts superclass token-manager threads, and logs startup. Each SQL operation delegates through the retry handler, obtains a connection, prepares a statement, binds parameters, and executes. Token cleanup selects stale token rows by `modifiedTime`. Counter operations delegate to `DistributedSQLCounter`.

## State, Persistence, And Dependencies
Durable state lives in SQL tables: `Tokens`, `DelegationKeys`, `LastSequenceNum`, and `LastDelegationKeyId`. Process state includes superclass token caches and background threads plus the connection pool. Dependencies include JDBC, Hadoop delegation token classes, and the retry handler.

## Integration Points
`RouterSecurityManager` reaches this implementation through `FederationUtil.newSecretManager`. It plugs into Hadoop's `SQLDelegationTokenSecretManager` abstract persistence hooks.

## Risks
Required schema must exist and column names/types must match. Constructor wraps thread-start `IOException` in `RuntimeException`, so configuration failures can fail router startup hard. `selectStaleTokenInfos` uses `setMaxRows` rather than SQL `LIMIT`, which depends on driver behavior. Retry wraps all SQLExceptions as retryable before the retry policy decides, which may retry non-transient SQL errors.

## Test Signals
Tests should exercise full token/key CRUD, stale-token selection, distributed counter reservation, retry policy behavior, schema-missing failures, stop closing the connection factory, and interoperability across two manager instances sharing one database.
