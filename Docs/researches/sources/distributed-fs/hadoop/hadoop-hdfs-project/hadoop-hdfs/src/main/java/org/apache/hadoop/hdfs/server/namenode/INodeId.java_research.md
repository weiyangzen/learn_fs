<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java

## Purpose

`INodeId` is the NameNode's sequential allocator for globally unique inode ids. It reserves a low range for compatibility/future use and defines the root inode id.

## Important APIs and Types

The class extends `SequentialNumber` and defines `LAST_RESERVED_ID` as `1 << 14`, `ROOT_INODE_ID` as `16385`, and `INVALID_INODE_ID` as `-1`. Its package-private constructor starts the sequence at the root id.

## Control Flow, State, and Persistence

Allocation behavior comes from `SequentialNumber`; this class only fixes constants and the starting value. The ids are persistent namespace identifiers used in FSImage, edit logs, block-collection ids, leases, and inode maps. They are intentionally not recycled.

## Dependencies and Integration Points

It integrates with all inode creation paths, `INodeMap` lookup, lease tracking by inode id, and block collection ownership. Compatibility with id `0` is noted in the class comment.

## Risks and Test Signals

Risk is low but compatibility-sensitive. Tests should verify root id stability, reserved-id boundaries, monotonic allocation across image load/save, and rejection or special handling of invalid ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeId.java -->
