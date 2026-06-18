<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MountTable.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MountTable.java

## Purpose
State Store schema for Router mount table entries that map federated source paths to one or more remote namespace destinations.

## APIs, Types, and Functions
Factory methods create entries from source path and destination map, set owner/group/mode from the current remote user, and initialize default quota. Abstract accessors cover source path, destinations, read-only flag, destination order, fault tolerance, owner/group/mode, and quota. Shared logic includes `getDefaultLocation()`, `like()`, `toString()`, primary key, `validate()`, `equals()`, `hashCode()`, `isAll()`, and path normalization.

## Control Flow, State, and Persistence
Primary key is `sourcePath`. Creation normalizes source/destination paths, converts destinations to `RemoteLocation`, sets ACL defaults, sets quota defaults, and validates. Validation enforces absolute source/destination paths, non-empty destinations, valid nameservice IDs, and fault-tolerant restrictions: multiple destinations and an ALL-style order.

## Dependencies and Integration
Used by mount table stores, Router admin, quota logic, resolvers, and balancing. Depends on Hadoop `Path`, `FsPermission`, `RemoteLocation`, `DestinationOrder`, `RouterQuotaUsage`, `RouterPermissionChecker`, `NameNode.getRemoteUser()`, and PB storage via `MountTablePBImpl`.

## Risks and Test Signals
Factory methods depend on current remote user context. `equals()`/`hashCode()` assume quota is non-null. Fault tolerance validation is tightly coupled to `DestinationOrder.FOLDER_ALL`. Tests around add/update/remove, ACLs, quota, multi-destination order, and cache refresh are essential.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/server/federation/store/records/MountTable.java -->
