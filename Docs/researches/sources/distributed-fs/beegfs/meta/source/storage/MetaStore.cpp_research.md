# sources/distributed-fs/beegfs/meta/source/storage/MetaStore.cpp

## Purpose

`MetaStore.cpp` implements the main metadata-server façade for POSIX-like operations on BeeGFS metadata: reference/release, open/close, stat, setattr, create, unlink, hardlink, inode deinline/reinline, fsck enumeration, raw metadata resync, and file state updates. It coordinates `InodeDirStore`, global and per-directory `InodeFileStore` instances, disposal directories, global inode locks, and on-disk metadata formats.

## Important APIs and Functions

Reference APIs include `referenceDir`, `releaseDir`, `referenceFile`, `referenceFileUnlocked`, `referenceLoadedFile`, `tryReferenceFileWriteLocked`, `releaseFile`, and `referenceInode`. Open/close APIs include `openFile`, `tryOpenFileWriteLocked`, and `closeFile`. Metadata operations include `stat`, `setAttr`, `incDecLinkCount`, `setDirParent`, `mkMetaFileUnlocked`, `mkNewMetaFile`, `makeDirInode`, and `removeDirInode`.

Unlink and disposal flows include `fsckUnlinkFileInode`, `unlinkInode`, `unlinkFile`, `unlinkFileInode`, `unlinkDirEntryWithInlinedInodeUnlocked`, `unlinkDentryAndInodeUnlocked`, `unlinkInodeLater`, and `insertDisposableFile`. Repair and hardlink APIs include `linkInSameDir`, `makeNewHardlink`, `verifyAndMoveFileInode`, `deinlineFileInode`, `reinlineFileInode`, and `checkAndRepairDupFileInode`. Fsck/resync paths include `getAllInodesIncremental`, `getAllEntryIDFilesIncremental`, `getRawMetadata`, `beginResyncFor`, and `unlinkRawMetadata`. `setFileState` integrates file-state changes with `GlobalInodeLockStore`.

## Control Flow and State

`MetaStore` uses its `rwlock` mostly as a shared/exclusive operation lock. File references first try the global file store, then fall back to a parent directory and its file store. Non-inlined file inodes should live in the global store; when stale client `EntryInfo` claims an inode is inlined but on-disk metadata shows otherwise, reference/open paths release the per-directory reference and retry under a write lock after moving the referencer to the global store.

`openFile` optionally checks disposal first for session restore, then follows global, non-inlined, or per-directory paths. `closeFile` writes dynamic metadata, releases file references, and maintains parent directory references for inlined/per-directory inodes. Creation builds an inlined dentry with `FileInodeStoreData`, applies default ACLs, inherits buddy mirroring, and optionally persists remote storage targets after referencing the new inode.

Unlink flows first remove dentries, then handle inode link count and busy state. Busy last-link files are moved or linked into disposal so storage chunks can be cleaned after close. Hardlink creation de-inlines inodes first, moves references to the global store, increments link count only when the inode is not a disposal inode, and returns the updated count. Deinline writes a non-inlined inode, copies RSTs and user xattrs, then updates the dentry; reinline copies inode data back into the dentry, restores the dentry-by-entryID hard link, and removes the standalone inode.

`setFileState` inserts the inode into `GlobalInodeLockStore` with `FILE_STATE_UPDATE`, references the inode with lock-store checks bypassed, validates active sessions in `FileInode::setFileState`, persists the state, and releases resources in reverse order.

## Persistence and Dependencies

The implementation delegates durable storage to `DirInode`, `DirEntry`, `FileInode`, `FileInodeStoreData`, `MetaStorageTk`, `StorageTkEx`, xattr/file-content APIs, and POSIX directory iteration. It uses `Program` for config, local node IDs, buddy group IDs, disposal directories, metadata paths, and ACL settings. Raw resync honors the xattr-versus-file-content storage mode.

## Integration Points

This file is the integration hub for metadata network message handlers and jobs. `MsgHelperStat`, `MsgHelperMkFile`, and xattr helpers feed operations here. Fsck consumes incremental inode enumeration. Buddy resync uses raw metadata helpers and `IncompleteInode`. Chunk balancing and HSM/file-state workflows coordinate through `GlobalInodeLockStore`.

## Risks and Test Signals

Risk is high because this code encodes lock ordering, lifetime ownership, and recovery from failed operations. Comments identify races involving stale inline flags, rename versus hardlink, disposal link count underflow, and deleting active inodes. Tests should exercise global/per-directory migration, open/close with stale inline flags, disposal cleanup for open files, hardlink deinline with concurrent rename mismatch, deinline rollback after xattr/RST failure, reinline duplicate cleanup, fsck enumeration for mirrored/non-mirrored paths, raw metadata in both xattr and content modes, and file-state lock release on every error path.
