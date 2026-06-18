# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/HikariDataSourceConnectionFactory.java

## Purpose
`HikariDataSourceConnectionFactory` adapts Hadoop configuration into a HikariCP JDBC connection pool for the SQL token secret manager.

## Important APIs, Types, And Functions
The constructor reads connection URL, username, password, driver class, and all properties under the Hikari prefix. Public methods implement `getConnection()` and `shutdown()`. `getDataSource()` is visible for tests.

## Control Flow
Construction builds a `Properties` object, resolves the configured password via `DFSUtil.getPassword`, merges Hikari-specific properties, creates `HikariConfig`, and creates `HikariDataSource`. Calls to `getConnection` delegate to the pool; shutdown closes it.

## State, Persistence, And Dependencies
State is the in-process Hikari data source and pooled JDBC connections. Persistence is provided by the external SQL database. Dependencies include HikariCP, Hadoop `Configuration`, and SQL token-manager config keys.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` uses this factory by default. `SQLConnectionFactory.getConnection(boolean)` wraps it to set autocommit for transactional counter operations.

## Risks
Missing or bad JDBC config fails at construction or first connection. Password handling depends on Hadoop credential provider resolution. Pool sizing and timeouts are entirely configuration-driven.

## Test Signals
Tests should verify property mapping, password resolution, Hikari prefix passthrough, connection acquisition, autocommit adjustment through the interface default, and datasource closure.
