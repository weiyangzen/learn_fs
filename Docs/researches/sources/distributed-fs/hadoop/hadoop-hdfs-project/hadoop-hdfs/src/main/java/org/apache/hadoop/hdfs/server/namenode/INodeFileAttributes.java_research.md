<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java -->
# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java

## Purpose

`INodeFileAttributes` is the read-only attribute contract for file inodes and snapshot copies. It lets snapshot and edit/image code reason about file metadata without requiring a live mutable `INodeFile`.

## Important APIs and Types

The interface exposes replication, striped/contiguous block type, EC policy id, preferred block size, packed header, local storage policy id, and `metadataEquals`. The nested `SnapshotCopy` extends `INodeAttributes.SnapshotCopy` and stores only the packed file `header` in addition to inherited permission/timestamp/ACL/XAttr snapshot fields.

## Control Flow, State, and Persistence

`SnapshotCopy` builds the same packed header as `INodeFile` through `INodeFile.HeaderFormat`, preserving file layout information for FSImage/snapshot diffs. Its methods decode from the stored header and do not track live block arrays. For non-striped files, `getErasureCodingPolicyID` returns `-1`, while the live `INodeFile` returns the replication policy id constant; callers need to tolerate that distinction.

## Dependencies and Integration Points

The contract is consumed by snapshot diff code, FSImage serialization paths, and file metadata comparisons. It depends on `PermissionStatus`, `BlockType`, `AclFeature`, `XAttrFeature`, and the `HeaderFormat` logic in `INodeFile`.

## Risks and Test Signals

The main risk is divergence between live inode header semantics and snapshot-copy header semantics. Tests should compare live and snapshot metadata equality, verify header round-trips for replicated and striped files, and ensure storage policy and ACL/XAttr references are preserved or intentionally shared as expected by snapshot code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/INodeFileAttributes.java -->
