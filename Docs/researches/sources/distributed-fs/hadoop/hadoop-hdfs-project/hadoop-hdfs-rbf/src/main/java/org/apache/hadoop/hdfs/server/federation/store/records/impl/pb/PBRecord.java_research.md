<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/PBRecord.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/PBRecord.java

## Purpose
Common marker/interface for protobuf-backed State Store records and protocol objects.

## APIs, Types, and Functions
Defines `Message getProto()`, `void setProto(Message)`, and `void readInstance(String)` with `IOException` on deserialization failures.

## Control Flow, State, and Persistence
The interface standardizes how serializers and debug tooling obtain concrete protobuf messages or populate records from base64-encoded serialized data. Implementations usually delegate to `FederationProtocolPBTranslator`.

## Dependencies and Integration
Implemented by PB record classes and many PB protocol request/response classes. `RouterAdmin.dumpStateStore()` uses it to print protobuf text for persisted records.

## Risks and Test Signals
`setProto(Message)` is weakly typed at the interface level, so implementations rely on translator runtime checks/casts. Compile-time implementation coverage and serializer round-trip tests are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/impl/pb/PBRecord.java -->
