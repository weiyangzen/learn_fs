# sources/distributed-fs/alluxio/core/server/master/src/main/java/alluxio/master/file/meta/UfsSyncUtils.java

## Purpose
`UfsSyncUtils` provides pure decision helpers for reconciling an Alluxio inode with a UFS fingerprint. Its main output is a `SyncPlan` saying whether to update metadata, delete the inode, load metadata, and/or sync directory children.

## Important APIs, types, and functions
`computeSyncPlan(Inode, Fingerprint, boolean)` is the main API. `inodeUfsIsContentSynced` checks persisted/unpersisted content presence and fingerprint content matching. `inodeUfsIsMetadataSynced` checks metadata fingerprint matching. Nested `SyncPlan` exposes read methods `toDelete()`, `toUpdateMetaData()`, `toLoadMetadata()`, and `toSyncChildren()`.

## Control flow
The method parses the inode's stored UFS fingerprint and validates it. If content and metadata match, persisted directories sync children and everything else is a no-op. If a directory is out of sync but the UFS side is also a directory or the subtree contains a mount point, the plan updates directory metadata unless the inode is root and then syncs children. For file mismatches, or directory-vs-nondirectory mismatches, unsynced content causes delete and optional metadata load if UFS exists; metadata-only differences cause update-metadata.

## State and persistence behavior
This class has no state or persistence. It interprets persisted inode fields such as `isPersisted`, `getUfsFingerprint`, parent id, and directory/file type.

## Dependencies and integration points
It depends on `Inode`, `InodeTree.NO_PARENT`, and `alluxio.underfs.Fingerprint`. `InodeSyncStream` and file-master sync code consume `SyncPlan` to perform actual deletes, metadata loads, and child sync traversal.

## Risks
An invalid stored inode fingerprint triggers a precondition failure. Root directory metadata is intentionally not updated from UFS, which is a special-case behavior tests should preserve. Mount-point containment prevents delete/reload of directories, so incorrect `containsMountPoint` input has high behavioral impact.

## Test signals
Tests should cover persisted file matches/mismatches, unpersisted absent UFS, UFS missing for persisted inodes, directory metadata-only changes, directory-vs-file conflicts, root directory handling, mount-point containment, invalid fingerprints, and each `SyncPlan` flag combination.
