<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/DisabledNameservice.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/DisabledNameservice.java

## Purpose
State Store record marking a nameservice as administratively disabled and therefore unavailable for routing.

## APIs, Types, and Functions
Provides `newInstance()`, `newInstance(String)`, abstract `getNameserviceId()`, and `setNameserviceId(String)`. Primary key map contains `nameServiceId`.

## Control Flow, State, and Persistence
New records are serializer-created and initialized with base timestamps. The nameservice ID is the only logical field, and `hasOtherFields()` returns false to tell tests/drivers that updates beyond the key are not expected. Expiration is disabled with `-1`.

## Dependencies and Integration
Used by nameservice disable/enable APIs and `NameserviceManager`. Concrete persistence is provided by `DisabledNameservicePBImpl` and `DisabledNameserviceRecordProto`.

## Risks and Test Signals
The abstract class does not validate empty IDs directly, so callers and concrete stores must avoid invalid disabled rows. Tests around `-nameservice disable/enable` and `getDisabledNameservices` exercise persistence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/DisabledNameservice.java -->
