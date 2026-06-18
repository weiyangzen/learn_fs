<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/AddMountAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/AddMountAttributes.java

## Purpose
Mutable command-parsing data holder for Router admin add/addAll mount operations, with helper methods to create or update `MountTable` records.

## APIs, Types, and Functions
Stores mount source, nameservices, destination, read-only flag, fault-tolerant flag, destination order, ACL info, and current parameter index. Key methods are `getMountTableEntryWithAttributes()`, `getNewOrUpdatedMountTableEntryWithAttributes(MountTable)`, private `getMountTableForAddRequest()`, and `updateCommonAttributes()`.

## Control Flow, State, and Persistence
For new entries, it normalizes the mount, builds a linked namespace-to-destination map to preserve order, creates a `MountTable`, applies optional attributes, and validates. For existing entries, it appends requested destinations, applies common attributes, and validates. Persistence happens later through Router admin requests.

## Dependencies and Integration
Used by `RouterAdmin.getAddMountAttributes()`, `addMount()`, and `addAllMount()`. Depends on `MountTable`, `DestinationOrder`, `FsPermission` via `RouterAdmin.ACLEntity`, and `RouterAdmin.normalizeFileSystemPath()`.

## Risks and Test Signals
`updateCommonAttributes()` assumes `aclInfo` is non-null. Existing-entry addition returns null after printing if any duplicate destination is found. Tests should cover addAll parsing, duplicate destinations, ACL application, fault-tolerant validation, and order preservation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-rbf/src/main/java/org/apache/hadoop/hdfs/tools/federation/AddMountAttributes.java -->
