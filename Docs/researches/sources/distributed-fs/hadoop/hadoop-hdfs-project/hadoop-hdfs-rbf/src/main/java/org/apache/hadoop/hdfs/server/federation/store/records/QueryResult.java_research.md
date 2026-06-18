<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/QueryResult.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/QueryResult.java

## Purpose
Immutable holder for State Store query results plus the driver timestamp associated with the data.

## APIs, Types, and Functions
Parameterized as `QueryResult<T extends BaseRecord>`. Constructor accepts a `List<T>` and `long timestamp`; getters return both fields.

## Control Flow, State, and Persistence
There is no transformation or validation. Stores use it to return records and a time basis for cache freshness, expiration, and downstream consistency checks.

## Dependencies and Integration
Used by State Store drivers and record stores that need to report result data and driver time together.

## Risks and Test Signals
The list is not defensively copied, so callers can mutate it after construction. Tests should verify timestamp propagation and expected record ordering/filtering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/QueryResult.java -->
