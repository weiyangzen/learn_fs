# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/protocol/SnapshotInfo.java

Purpose: Carries snapshot metadata for protocol/JMX/UI style consumers, including a nested bean representation used for snapshot status exposure.

Important APIs and types: `SnapshotInfo` stores snapshot name, root, creation time string, protobuf permission, owner, and group with final getters and `toString()`. Nested `Bean` stores snapshot ID, snapshot directory, modification time, and a status string derived from deletion marking.

Control flow: Construction stores supplied immutable fields. `Bean` maps `isMarkedAsDeleted` to status `DELETED` or `ACTIVE`.

State and persistence behavior: Instances are immutable value carriers except for referenced protobuf object immutability. They do not modify namespace state; they serialize/expose snapshot metadata gathered elsewhere.

Dependencies and integration points: Depends on `AclProtos.FsPermissionProto` and HDFS snapshot management/reporting paths. The bean shape is likely consumed by JSON/JMX-style reflection.

Risks: Time fields use different representations between `SnapshotInfo` (`String`) and `Bean` (`long`), so consumers must not conflate them. `toString()` includes permission/owner/group details. Status is stringly typed and must stay consistent with external expectations.

Test signals: Tests should verify getters, string rendering, permission propagation, bean status for active/deleted snapshots, and JSON/JMX serialization compatibility.
