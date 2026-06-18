# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs/src/main/java/org/apache/hadoop/hdfs/server/namenode/snapshot/FSImageFormatPBSnapshot.java

## Purpose

`FSImageFormatPBSnapshot` reads and writes snapshot-related sections in the protobuf FSImage format. It persists snapshottable directories, snapshots, inode references, file diffs, directory diffs, created/deleted lists, snapshot inode copies, block lists needed for snapshot truncation, and nonfatal image validation errors.

## Important APIs, Types, And Functions

The nested `Loader` exposes `loadINodeReferenceSection`, `loadSnapshotSection`, and `loadSnapshotDiffSection`, with helpers for `loadFileDiffList`, `loadCreatedList`, `loadDeletedList`, and `loadDirectoryDiffList`. The nested `Saver` exposes `serializeSnapshotSection`, `serializeINodeReferenceSection`, `serializeSnapshotDiffSection`, `serializeFileDiffList`, `serializeDirDiffList`, `buildINodeReference`, and `getNumImageErrors`.

## Control Flow

Loading first reconstructs inode references into the loader context reference list. Snapshot section loading restores `SnapshotManager` counters, marks directories as snapshottable, adds them to the manager, then loads snapshot roots and inserts snapshots into parent features. Snapshot diff loading reads entries keyed by inode ID and dispatches to file or directory diff loaders. Saving writes snapshottable directory IDs and snapshot roots, later serializes references from the saver context, and scans the inode map to emit file and directory diff entries. Diff lists are written in reverse order and loaded with `addFirst` to restore chronological order.

## State And Persistence Behavior

The protobuf image persists static snapshot state for NameNode restart. File diffs persist snapshot ID, file size, optional file attribute copy, and optional contiguous blocks. Directory diffs persist snapshot ID, child size, snapshot-root flag, optional directory copy, created-list names, and deleted inode IDs or reference indices. The saver counts missing referred inode IDs, repeated deleted-list names, and misordered deleted-list entries as image errors rather than throwing immediately.

## Dependencies And Integration Points

The class integrates with `FSImageFormatProtobuf`, protobuf `FsImageProto` sections, `FSImageFormatPBINode` attribute builders/loaders, `SnapshotManager`, `FSDirectory`, `INodeMap`, `BlockManager`, `INodeReference`, ACL/XAttr/quota loaders, and `SaveNamespaceContext` cancellation. It is the protobuf counterpart to the older `SnapshotFSImageFormat`.

## Risks And Edge Cases

Order is critical: created lists store only names and must resolve to current children or posterior deleted entries; deleted reference indices must match the reference section order. Loading file diffs assumes persisted file-diff blocks are contiguous and reconstructs missing block-map entries. Directory deleted lists are sorted after load, while save detects repeated or misordered entries. Striped-file attributes are handled differently from replication attributes. Cancellation may split snapshot diff sections into subsections.

## Test Signals

Tests should save and load snapshots with file truncation blocks, deleted references, ACLs, XAttrs, quotas, striped and replicated files, repeated/misordered deleted-list validation, missing referred inode detection, large inode-map snapshot diff subsection rollover, and equivalence between pre-save and post-load snapshot listings and diff reports.
