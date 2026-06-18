<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/Query.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/Query.java

## Purpose
Generic partial-record query wrapper for State Store records.

## APIs, Types, and Functions
Parameterized as `Query<T extends BaseRecord>`. Stores a final partial record, exposes `getPartial()`, `matches(T)`, and `toString()`.

## Control Flow, State, and Persistence
`matches()` returns false for a null partial; otherwise it delegates to `partial.like(other)`. Matching semantics are therefore record-specific, allowing full primary-key equality for default records and partial-field matching for membership, router, and mount table records.

## Dependencies and Integration
Used by State Store drivers and cached record stores to filter rows. Depends only on `BaseRecord`.

## Risks and Test Signals
The direction of comparison matters: `partial.like(other)` lets partial fields be null wildcards only if the partial record's `like()` implements that pattern. Driver query tests and partial membership/mount queries are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/Query.java -->
