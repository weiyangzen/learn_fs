# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileUnderConstructionFeature.java

## sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/FileUnderConstructionFeature.java

Purpose: `FileUnderConstructionFeature` is the feature attached to an `INodeFile` while a client lease is still writing the file. It stores lease identity and provides helpers for mutating the last under-construction block during length update and deletion cleanup.

Important APIs and types: the class implements `INode.Feature`. It stores mutable `clientName` and final `clientMachine`, exposes getters, has package-scope `setClientName`, `updateLengthOfLastBlock`, and `cleanZeroSizeBlock`. It interacts directly with `INodeFile`, `BlockInfo`, and `INode.BlocksMapUpdateInfo`.

Control flow: construction records the lease holder and client machine. `updateLengthOfLastBlock` fetches the file's last block, asserts it exists and is not complete, then sets the reported byte length. `cleanZeroSizeBlock` checks whether the file has a trailing incomplete block, and if that block is zero bytes, records it for block-map deletion and removes it from the file.

State and persistence behavior: this feature is in-memory inode state but is part of the NameNode namespace model that can be represented in fsimage/edit-log operations through the owning file. The client machine is immutable after construction; client name can be updated, for example during lease recovery. Block length and removal mutate the owning file/block state.

Dependencies and integration points: it is used by `INodeFile` and lease-management/recovery paths, and its cleanup feeds `BlocksMapUpdateInfo` so the block manager can delete stale zero-length under-construction blocks. Snapshot-aware deletion paths rely on it when a current file also has snapshot history.

Risks: assertions protect against impossible states but are disabled in normal JVM operation, so callers must ensure the last block is present and under construction. Removing a zero-sized UC block must stay coordinated with block-map cleanup or stale blocks can remain. Length updates trust client-reported length and depend on higher-level validation.

Test signals: tests should cover lease holder mutation, last-block length update, assertion/error behavior for missing or complete blocks, zero-size UC block collection/removal, nonzero UC blocks remaining, and interaction with snapshot deletion cleanup.
