# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsLocatedFileStatus.java

## Purpose
`HdfsLocatedFileStatus` is a `LocatedFileStatus` implementation carrying HDFS-specific metadata and optional `LocatedBlocks`. Directories and symlinks may also be represented as this class for backward compatibility.

## APIs and Behavior
The constructor initializes superclass `LocatedFileStatus` using converted permission and attribute flags, then stores local path bytes, symlink bytes, inode ID, child count, file encryption info, storage policy, EC policy, and transient HDFS block locations. `makeQualifiedLocated()` qualifies the path and converts `LocatedBlocks` into user-facing `BlockLocation[]`. It exposes namespace get/set and HDFS-specific getters.

## State, Dependencies, and Integration
It depends on `DFSUtilClient`, `FileEncryptionInfo`, `ErasureCodingPolicy`, and `LocatedBlocks`. The `hdfsloc` field is transient, so serialized forms depend on superclass block locations after qualification.

## Risks and Test Signals
`setGroup(String)` calls `super.setOwner(group)`, which appears to set the owner instead of the group. Raw path/symlink arrays are returned without copies. Tests should cover group setter behavior, symlink detection and error path, block-location conversion before/after `makeQualifiedLocated`, serialization of transient locations, namespace preservation, and mutation of returned byte arrays.
