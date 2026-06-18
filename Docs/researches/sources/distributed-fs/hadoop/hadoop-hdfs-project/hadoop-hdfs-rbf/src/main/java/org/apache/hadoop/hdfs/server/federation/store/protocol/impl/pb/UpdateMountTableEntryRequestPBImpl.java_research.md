<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateMountTableEntryRequestPBImpl.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateMountTableEntryRequestPBImpl.java

## Purpose
PB request for replacing or updating an existing mount table entry in the State Store.

## APIs, Types, and Functions
Wraps `UpdateMountTableEntryRequestProto`. `getEntry()` converts nested `MountTableRecordProto` into a serializer-created `MountTablePBImpl`; `setEntry(MountTable)` accepts only `MountTablePBImpl` and writes proto field `entry`.

## Control Flow, State, and Persistence
Admin and balancing code mutate a `MountTable` record, validate it at the record layer, place it in this request, and call `updateMountTableEntry`. Server code extracts the entry and persists the changed mount table row keyed by `sourcePath`.

## Dependencies and Integration
Depends on `StateStoreSerializer`, `MountTable`, `MountTablePBImpl`, and generated mount-table protos. It is used by `RouterAdmin.updateMount()`, quota updates, and `MountTableProcedure`.

## Risks and Test Signals
Non-PB serializers cause `IOException`; absent `entry` can become a default proto-backed record and fail later validation. Tests should cover destination changes, ACL changes, quota changes, and cache refresh after update.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/protocol/impl/pb/UpdateMountTableEntryRequestPBImpl.java -->
