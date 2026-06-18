<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java

## Purpose

`INodeSymlink` is the namespace inode for symbolic links. It stores a symlink target and participates in namespace counts, snapshots, content summaries, and visitor traversal without owning blocks.

## Important APIs and Types

The constructor stores the target as DFS byte encoding. `recordModification` snapshots the symlink through the parent directory, `getSymlinkString` and `getSymlink` expose the target, and `computeQuotaUsage` counts one namespace entry. ACL, XAttr, and storage policy operations throw `UnsupportedOperationException`.

## Control Flow, State, and Persistence

The persistent state is inherited inode metadata plus the immutable target byte array. Snapshot recording saves a copy into the parent snapshot diff when the symlink is in the latest snapshot. Deletion from current state with no prior snapshot removes the inode and adds a namespace quota delta. Content summary increments `Content.SYMLINK`.

## Dependencies and Integration Points

It integrates with `DFSUtil` byte/string conversion, `INodeDirectory.saveChild2Snapshot`, `Snapshot`, `QuotaCounts`, `ContentSummaryComputationContext`, and namespace visitors.

## Risks and Test Signals

Risks are around unsupported feature calls and snapshot preservation of immutable target bytes. Tests should cover symlink creation, snapshot then delete, content summary counts, quota counts, dump output, and explicit rejection of ACL/XAttr/storage policy operations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeSymlink.java -->
