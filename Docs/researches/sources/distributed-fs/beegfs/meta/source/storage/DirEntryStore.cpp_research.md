# sources/distributed-fs/beegfs/meta/source/storage/DirEntryStore.cpp

## Purpose

`DirEntryStore.cpp` implements the filesystem-backed directory-entry store for a BeeGFS metadata directory. A `DirEntryStore` maps a parent directory ID plus buddy-mirror state to an on-disk dentry directory, creates and removes that directory structure, persists individual `DirEntry` objects, links inode files into directories, removes file and directory dentries, lists directory contents using stable local-filesystem offsets, and updates dentry owner-node information.

The implementation is intentionally thin over POSIX metadata operations: `mkdir`, `rmdir`, `unlink`, `link`, `rename`, `opendir`, `seekdir`, `readdir`, `stat`, and `setxattr`-backed `DirEntry` helpers. It centralizes locking around those operations and adds BeeGFS-specific path derivation, serialization-size-aware listing, and buddy-resync change tracking.

## Important APIs and Functions

- `getDirEntryStoreDynamicEntryPath(parentID, isBuddyMirrored)` selects either the regular dentry root or buddy-mirror dentry root from `Program::getApp()` and builds the parent dentry path with `MetaStorageTk::getMetaDirEntryPath`.
- Constructors initialize `parentID`, `dirEntryPath`, and `isBuddyMirrored`; the default constructor leaves `parentID` as `"<undef>"` until `setParentID`.
- `mkDentryStoreDir(dirID, isBuddyMirrored)` creates the dentry content directory and its ID subdirectory. It returns `SUCCESS`, `EXISTS`, or `INTERNAL`.
- `rmDirEntryStoreDir(id, isBuddyMirrored)` removes the ID subdirectory and the content directory, treating `ENOENT` as non-fatal but logging unexpected errors.
- `makeEntry` and `makeEntryUnlocked` persist a `DirEntry` via `DirEntry::storeInitialDirEntry`.
- `linkInodeToDir` and `linkInodeToDirUnlocked` hard-link a separate inode-file path into the directory under a filename, used for disposal or reinsertion workflows.
- `removeDir` and `removeDirUnlocked` load a dentry, verify it is a directory, and remove it through `DirEntry::removeDirDentry`.
- `unlinkDirEntry` and `unlinkDirEntryUnlocked` remove file dentries through `DirEntry::removeFileDentry`, with caller-supplied unlink flags controlling filename and ID-link deletion.
- `linkEntryInDir` creates a same-directory hardlink between two inlined inode dentries. The caller must have already incremented the file link count.
- `renameEntry` performs a simple same-directory POSIX rename.
- `listIncrementalEx` lists dentries with stable `telldir`/`seekdir` offsets and can stop by serialized response size when `availableRespBufSize` is non-zero.
- `listIDFilesIncremental` lists the dentry-by-ID subdirectory, supporting direct server offsets and a slower incremental-offset fallback for fsck/client seek cases.
- `exists`, `getEntryData`, `dirEntryCreateFromFile`, `setOwnerNodeID`, and `setParentID` are lookup and metadata mutation helpers.

## Control Flow

Most public mutators acquire `rwlock` in write mode, call an `Unlocked` implementation, then release the lock. Read operations use read mode. `mkDentryStoreDir` and `rmDirEntryStoreDir` are static helpers and do not use instance locking because they operate on explicit IDs during lifecycle operations.

Directory-store creation first creates the parent content directory, then creates the dentry-by-ID subdirectory. If the second creation fails, it attempts to remove the first directory before returning an internal error. Removal runs in the reverse order: ID subdirectory first, content directory second.

Listing is offset-driven. `listIncrementalEx` opens the dentry directory, seeks to the caller-provided native offset if non-zero, then loops over `StorageTk::readdirFilteredEx`. For each entry it optionally loads dentry metadata to populate type and entry ID. When `availableRespBufSize` is set, it estimates the serialized contribution of the current entry and stops before overflowing the response budget. The new server offset is the last returned `dirent::d_off`.

`getEntryData` loads a `DirEntry`, optionally copies its inlined `FileInodeStoreData`, clears the source pattern pointer to avoid double deletion, builds `EntryInfo` flags for inlined and buddy-mirrored entries, and returns `SUCCESS` or `PATHNOTEXISTS`.

## State and Persistence Behavior

Persistent state is represented by the local filesystem tree:

- A dentry content directory under either `dentriesPath` or `buddyMirrorDentriesPath`.
- A dentry-by-ID subdirectory derived by `MetaStorageTk::getMetaDirEntryIDPath`.
- Per-entry files and hardlinks written by `DirEntry` methods.

The class keeps in-memory identity fields only: `parentID`, `dirEntryPath`, `isBuddyMirrored`, and an `RWLock`. It does not cache directory contents. All existence, listing, and metadata retrieval go back to disk.

For buddy-mirrored stores, successful creation, deletion, linking, renaming, and metadata changes enqueue changes in `BuddyResyncer::getSyncChangeset()` using `MetaSyncFileType::Directory`, `Dentry`, or `Inode` depending on the object touched.

## Dependencies and Integration Points

This file depends on `Program::getApp()` for configured metadata paths, `MetaStorageTk` for on-disk path layout, `DirEntry` for actual dentry serialization and deletion, `StorageTk` for filtered readdir, `System` and `LogContext` for diagnostics, and `BuddyResyncer` for mirror resync tracking.

`DirEntryStore` is a core component embedded in `DirInode`. `MetaStore` and `DirInode` are friends and call unlocked entry operations during higher-level rename, unlink, and directory lifecycle flows.

## Risks and Edge Cases

- `mkDentryStoreDir` uses `unlink` to remove a directory after ID-subdirectory creation fails; a directory normally requires `rmdir`, so that compensation path may not clean up as intended.
- `listIncrementalEx` computes response size from known list serialization fields but explicitly excludes message-level overhead, relying on the caller to pass a reduced budget.
- Offset behavior relies on local filesystem `d_off` stability. The comment explains this is needed for applications that unlink entries between `readdir` calls.
- `getEntryData` transfers a stripe-pattern pointer out of a temporary `DirEntry` by setting the source pattern to `NULL`; future changes to `FileInodeStoreData` ownership semantics could introduce double-free or leak hazards.
- `linkEntryInDir` requires the caller to adjust link counts before the hardlink operation to avoid crash windows with too-low link counts.
- Buddy-resync additions happen after some locks are released in several methods; the path strings are captured before unlock, but ordering with concurrent operations still matters.

## Test Signals

Useful tests include creating/removing dentry stores in both mirrored and unmirrored paths, exercising failure cleanup for partial directory creation, listing directories while unlinking returned entries, verifying buffer-size-limited listing boundaries, checking dentry-by-ID fsck listing offsets, validating inlined inode metadata returned by `getEntryData`, and confirming buddy-resync change records for directory, dentry, and inode operations.
