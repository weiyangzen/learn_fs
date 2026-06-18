# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/router/security/token/DistributedSQLCounter.java

## Purpose
`DistributedSQLCounter` coordinates monotonically allocated integer values across routers using a single-row SQL table.

## Important APIs, Types, And Functions
Public methods are `selectCounterValue`, `updateCounterValue(int)`, `updateCounterValue(int, Connection)`, and `incrementCounterValue(int)`. It stores the counter field name, table name, and `SQLConnectionFactory`.

## Control Flow
Reads execute `SELECT field FROM table`, optionally with `FOR UPDATE`. Updates execute `UPDATE table SET field = ?`. Increment disables autocommit, raises isolation to at least repeatable read, selects the row for update, calculates the new value, handles integer overflow by resetting from zero, updates the table, commits, and rolls back on failure.

## State, Persistence, And Dependencies
The durable state is the SQL table row. The class itself keeps only configuration strings and the connection factory. It depends on JDBC `Connection`, `Statement`, `PreparedStatement`, and `ResultSet`.

## Integration Points
`SQLDelegationTokenSecretManagerImpl` uses two counters for delegation token sequence numbers and delegation key IDs.

## Risks
The table and one initial row must already exist. SQL strings interpolate table and field names, so those names must be trusted constants. `FOR UPDATE` and isolation behavior are database-dependent. Overflow resets can reuse low values if not coordinated with existing records.

## Test Signals
Tests should cover missing row initialization errors, transaction rollback on update failure, concurrent increments, overflow behavior, autocommit modes, and database compatibility for `FOR UPDATE`.
