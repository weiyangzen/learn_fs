# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-client/src/main/java/org/apache/hadoop/hdfs/protocol/HdfsNamedFileStatus.java

## Purpose
`HdfsNamedFileStatus` is the non-located `FileStatus` implementation for HDFS metadata. It is used when a regular file status does not carry block locations.

## APIs and Behavior
The constructor passes converted permission and attribute flags to `FileStatus`, then stores local path bytes, symlink bytes, inode ID, child count, file encryption info, storage policy, and EC policy. It implements HDFS-specific getters, symlink conversion to `Path`, namespace accessors, and visible permission/owner/group setters.

## State, Dependencies, and Integration
It depends on `DFSUtilClient`, `FileEncryptionInfo`, `ErasureCodingPolicy`, and `HdfsFileStatus.convert`. It is produced by `HdfsFileStatus.Builder` for plain named file statuses and consumed by listing/status calls.

## Risks and Test Signals
Like the located variant, `setGroup(String)` calls `super.setOwner(group)`, apparently overwriting owner instead of group. Raw byte arrays are returned. Tests should cover group setter correctness, local/full path behavior, symlink error handling, default flag conversion, namespace fields, and equality/hash delegating to `FileStatus`.
