# sources/distributed-fs/beegfs/meta/source/storage/DirInode.cpp

## Purpose

`DirInode.cpp` implements BeeGFS directory inode behavior: default file striping, persistent directory metadata storage and loading, dentry creation/removal/listing delegation, directory counters and stat data, remote storage target metadata, xattr operations, parent/owner updates, and buddy-mirror conversion for contained inlined file inodes.

The class combines durable inode metadata with a `DirEntryStore`. Directory metadata is stored either in a metadata file's extended attribute (`META_XATTR_NAME`) or in file contents, according to `storeUseExtendedAttribs`. Child dentries live in the per-directory dentry directory managed by `DirEntryStore`.

## Important APIs and Functions

- The creation constructor initializes IDs, owner, feature flags, default stripe pattern clone, zero child counters, embedded `DirEntryStore`, and `StatData` for a new directory.
- `createFileStripePattern` and `createFileStripePatternUnlocked` choose storage targets from storage pools and capacity pools, applying default directory settings, caller overrides, buddy-mirror handling, target limits, and optional RAID10 mirror-target rotation.
- `setStripePattern` updates the directory default pattern. Non-root actors may only change default target count and chunk size, not pool or pattern type.
- `setRemoteStorageTarget`, `clearRemoteStorageTarget`, `storeRemoteStorageTargetInfoUnlocked`, `storeRemoteStorageTargetDataBufAsXAttr`, and `loadRstFromFileXAttr` manage remote storage target xattrs and the `DIRINODE_FEATURE_HAS_RST` flag.
- `listIncremental`, `listIncrementalEx`, `listIDFilesIncremental`, `exists`, and `getEntryData` delegate to the embedded `DirEntryStore`.
- `makeDirEntry`, `linkFilesInDirUnlocked`, `linkFileInodeToDir`, `removeDir`, `renameDirEntry`, `unlinkDirEntry`, and `unlinkBusyFileUnlocked` coordinate child dentry changes with directory counters, timestamps, and resync notices.
- `refreshMetaInfo` and `refreshSubentryCountUnlocked` recalculate subdirectory and file counts by listing dentries and reading their types.
- `storeInitialMetaData`, `storeInitialMetaData(defaultACL, accessACL)`, and `storeInitialMetaDataInode` create the dentry store and directory inode file, optionally adding ACL xattrs.
- `storeUpdatedMetaDataBuf*` and `storeUpdatedMetaDataUnlocked` serialize and update directory inode metadata through xattrs, temp-file rename, or in-place fallback.
- `loadIfNotLoaded`, `invalidate`, `loadFromFile`, `loadFromFileXAttr`, `loadFromFileContents`, and `createFromFile` implement lazy and explicit loading.
- `getStatData`, `setStatData`, `setAttrData`, `setDirParentAndChangeTime`, `setOwnerNodeID`, `listXAttr`, `getXAttr`, `removeXAttr`, and `setXAttr` expose inode metadata and xattr operations.
- `setIsBuddyMirrored` flips the directory feature flag, retargets the dentry store path, iterates all inlined dentries, updates their buddy-mirror flags, loads corresponding `FileInode` objects, and updates those inodes.

## Control Flow

Most public methods acquire `rwlock` in read or write mode and call an unlocked helper. Lazy-load paths check `isLoaded` and call `loadFromFile` before using metadata that may not be in memory. `loadFromFile` chooses xattr or file-content deserialization and marks the inode loaded on success.

Directory creation is two-stage. `storeInitialMetaData` creates the dentry directory structure first, then writes the inode metadata file. If inode creation fails after directory creation, it removes the dentry store unless the inode file already exists, which is treated as a successful race. The ACL overload then writes default and access ACL xattrs.

Metadata updates serialize the full `DirInode` through `DiskMetaData::serializeDirInode`. With xattrs enabled, the serialized blob is written to `META_XATTR_NAME`. With content storage, the code writes to a `.update` file and renames it over the inode file. On `ENOSPC` or short writes due to space pressure, it falls back to in-place update after `posix_fallocate`.

Child dentry operations delegate to `DirEntryStore`, then update counters and timestamps if the dentry operation succeeded. Counter update failures are sometimes returned as `INTERNAL` and sometimes only logged depending on operation semantics.

## State and Persistence Behavior

In-memory state includes directory identity, owner and parent node IDs, feature flags, default `StripePattern`, `RemoteStorageTarget`, `StatData`, `numSubdirs`, `numFiles`, `exclusive`, `isLoaded`, `loadLock`, `fileStore`, and the embedded `DirEntryStore`.

Persistent state includes:

- The directory inode metadata file under regular or buddy-mirror inode paths.
- The serialized `DirInode` blob in either `META_XATTR_NAME` or file contents.
- Optional `RST_XATTR_NAME` with serialized remote storage target data, xattr-only.
- The per-directory dentry store directory and dentry-by-ID directory.
- Optional ACL/user xattrs on either the directory dentry path or child file dentry-by-ID path.

The directory stat response derives `nlink` as `2 + numSubdirs` and file size as `numSubdirs + numFiles`, which is important for tools like `find`.

Buddy-mirrored directories enqueue inode, dentry, or directory modifications/deletions in the current buddy-resync changeset after successful durable changes.

## Dependencies and Integration Points

`DirInode.cpp` depends on `Program`, configuration, storage pools, target capacity pools, `Raid0Pattern`, `Raid10Pattern`, `DirEntryStore`, `DirEntry`, `DiskMetaData`, `FileInode`, `MetaStore`, `XAttrTk`, `PosixACL`, and POSIX file/xattr APIs. It is a central integration point for namespace operations in `MetaStore`, fsck-style listing, ACL handling, remote storage target metadata, and buddy mirroring.

## Risks and Edge Cases

- The in-place metadata update fallback reduces the temp-file atomicity guarantee under low-space conditions. It uses `posix_fallocate` to reduce risk, but a crash during in-place write can still be more dangerous than rename.
- `setIsBuddyMirrored` explicitly warns that failure can leave a mix of mirrored and unmirrored contained items; callers need repair or retry handling.
- Counter updates after dentry changes are not always fatal. A successful unlink with failed counter persistence can leave count metadata stale until `refreshMetaInfo`.
- `setRemoteStorageTarget` and `clearRemoteStorageTarget` can update feature flags and xattrs in separate steps, creating possible inconsistency if one succeeds and the other fails.
- `createFileStripePatternUnlocked` returns null for missing storage pools or insufficient targets; callers must translate this to file-creation failure cleanly.
- Non-root `setStripePattern` mutates the existing object partially and restores only by retained clone on store failure; permission checks protect pool and pattern type but not all semantic stripe-policy concerns.
- Xattr methods for child files reference active `FileInode` handles through `MetaStore` to update change time, so lock ordering between directory, metastore, and file handles matters.

## Test Signals

Key tests should cover xattr and file-content metadata modes, create/update/load round trips, low-space update fallback, target selection for normal and buddy-mirror stripe patterns, storage pool missing/insufficient target failures, child dentry counter updates and `refreshMetaInfo`, ACL xattr creation, RST set/clear/load, stat `nlink` behavior, buddy-mirror resync recording, and partial-failure handling in buddy-mirror conversion.
