<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java

## Purpose

`INodeWithAdditionalFields` is the common mutable base for inodes with durable ids, local names, packed permissions, modification/access times, linked-set membership, and optional feature arrays.

## Important APIs and Types

`PermissionStatusFormat` packs mode, group serial number, and user serial number into a `long`; it also reconstructs `PermissionStatus` from a string table. The class implements `LightWeightGSet.LinkedElement` via `next`, exposes getters/setters for id/name/permission/times, and manages feature arrays through `addFeature`, `removeFeature`, and `getFeature`. ACL features are interned through `AclStorage`, and XAttr features are attached directly.

## Control Flow, State, and Persistence

The packed permission format is explicitly used in-memory and on-disk, so bit layout changes are incompatible. Snapshot-aware getters delegate to `getSnapshotINode(snapshotId)` when reading historical user/group/mode/times/ACL/XAttr. Feature mutation copies the feature array on add/remove; duplicates are rejected for ACL and XAttr. Copy construction preserves parent or parent reference and clones primitive fields but shares name bytes and feature array references according to existing inode-copy semantics.

## Dependencies and Integration Points

This base supports `INodeFile`, `INodeDirectory`, `INodeSymlink`, and temporary lookup keys in `INodeMap`. It depends on `SerialNumberManager`, `LongBitFormat`, `AclStorage`, `Snapshot`, and Hadoop permission types.

## Risks and Test Signals

Risks include on-disk incompatibility from packed format changes, duplicate/missing feature errors, snapshot getters returning live state accidentally, and shared feature-array semantics during copies. Tests should cover permission packing/unpacking with string tables, ACL feature interning/removal, XAttr addition/removal, timestamp snapshot reads, and `LinkedElement` behavior in `LightWeightGSet`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeWithAdditionalFields.java -->
