<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/StateStoreVersion.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/StateStoreVersion.java

## Purpose
Embedded record tracking Router-observed State Store version counters for membership and mount table data.

## APIs, Types, and Functions
Factory methods create an empty record or one populated with membership and mount table versions. Abstract accessors cover `membershipVersion` and `mountTableVersion`. `toString()` prints both counters.

## Control Flow, State, and Persistence
The record is not stored directly. It returns an empty primary-key map, disables expiration, and no-ops timestamp setters/getters. It is embedded inside `RouterState`.

## Dependencies and Integration
Used by Router heartbeat state to advertise cache/store version knowledge. Concrete PB mapping is `StateStoreVersionPBImpl` over `StateStoreVersionRecordProto`.

## Risks and Test Signals
Inherited base validation is unsuitable because timestamps are zero. Router heartbeat tests verify that version counters are included and update as expected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/StateStoreVersion.java -->
