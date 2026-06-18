<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateNamenodeRegistrationRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateNamenodeRegistrationRequestPBImpl.java

## Purpose
PB request for overriding a namenode registration's service state.

## APIs, Types, and Functions
Wraps `UpdateNamenodeRegistrationRequestProto`. Exposes `getNameserviceId()`, `getNamenodeId()`, `getState()`, and matching setters. `state` is stored as `FederationNamenodeServiceState.toString()` and parsed with `valueOf()`.

## Control Flow, State, and Persistence
Callers set the nameservice, namenode, and target state. The State Store or resolver layer uses those keys to find membership records and override their state. The request itself is transient; the resulting membership state may be persisted or cached depending on store behavior.

## Dependencies and Integration
Depends on `FederationNamenodeServiceState`, generated protos, and PB translator. It belongs to federation membership management, especially admin override and resolver state transitions.

## Risks and Test Signals
Invalid or missing state strings throw at `valueOf()` or default to empty strings from proto accessors. Tests should cover active/standby/unavailable/expired transitions and malformed state handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateNamenodeRegistrationRequestPBImpl.java -->
