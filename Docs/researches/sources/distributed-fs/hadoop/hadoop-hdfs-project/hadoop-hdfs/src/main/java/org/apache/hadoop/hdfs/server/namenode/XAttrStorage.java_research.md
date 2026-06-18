# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/XAttrStorage.java

## Purpose

`XAttrStorage.java` provides small static helpers for reading and replacing xattr features on inodes. The source was read as a complete 81-line file.

## Important APIs, Types, and Functions

The APIs are `readINodeXAttrByPrefixedName`, `readINodeXAttrs`, and `updateINodeXAttrs`.

## Control Flow

Read-by-name fetches the inode's `XAttrFeature` for a snapshot ID and delegates to `getXAttr`. Read-all fetches xattrs from `INodeAttributes` or returns an empty list. Update removes any existing feature from the inode, then adds a new `XAttrFeature` if the supplied list is non-empty.

## State and Persistence Behavior

The helpers mutate inode feature state under the caller's lock. Because inode feature state is serialized to fsimage and journaled by higher-level operations, replacing the feature is a persistent namespace mutation once logged.

## Dependencies and Integration Points

It integrates with `INode`, `INodeAttributes`, `XAttrFeature`, `XAttr`, and `QuotaExceededException`. Comments require callers to hold FSDirectory read or write locks as appropriate.

## Risks and Edge Cases

The update path removes before adding, so callers must ensure exceptions from adding a new feature are handled consistently by surrounding transaction logic. Locking is a caller contract, not enforced here.

## Test Signals

Tests should cover reading absent features, snapshot-specific reads, replacing existing xattrs, clearing with null/empty lists, quota exception propagation, and lock-contract coverage in higher-level xattr operations.
