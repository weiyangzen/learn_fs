# sources/distributed-fs/beegfs/meta/source/storage/InodeFileStore.cpp

## Purpose

`InodeFileStore.cpp` implements reference-counted storage for loaded `FileInode` objects. One instance exists globally in `MetaStore`, and each `DirInode` has a per-directory instance. The implementation handles file reference/open/close, stat/setattr, unlink, remote move serialization, hardlink count changes, global lock-store exclusion, and race repair around stale inline flags.

## Important APIs and Functions

Lookup and reference APIs include `isInStore`, `referenceLoadedFile`, `referenceFileInode`, `referenceFileInodeUnlocked`, `referenceFileInodeMapIterUnlocked`, and `getReferencerAndDeleteFromMap`. Lifecycle APIs include `releaseFileInode`, `closeFile`, `clearStoreUnlocked`, `loadAndInsertFileInodeUnlocked`, `insertReferencer`, and `deleteUnreferencedInodeUnlocked`. Mutation APIs include `openFile`, `stat`, `setAttr`, `unlinkFileInode`, `moveRemoteBegin`, `moveRemoteComplete`, `isUnlinkable`, and `incDecLinkCount`.

## Control Flow and State

The store owns a map from entry ID to `FileInodeReferencer*` protected by `rwlock`. `referenceFileInodeUnlocked` checks the map, optionally loads from disk, and normally refuses to load when `GlobalInodeLockStore` contains the inode. Internal operations can pass `checkLockStore=false`. `referenceFileInodeMapIterUnlocked` refuses references if another thread owns the inode's exclusive TID.

`openFile` references the inode, calls `FileInode::checkAccessAndOpen`, and releases the reference on access failure. `closeFile` persists dynamic metadata via `decNumSessionsAndStore`, detects the last writer close, and decrements the referencer. `unlinkFileInodeUnlocked` checks unlinkability, optionally clones an unreferenced inode for the caller, and removes persistent metadata. Remote move begin serializes an unreferenced inode, sets exclusive TID, persists original parent ID, and appends RST data if present. Remote complete deletes the unreferenced inode entry.

## Persistence and Dependencies

Persistent load/store is delegated to `FileInode::createFromEntryInfo`, `FileInode::unlinkStoredInodeUnlocked`, `FileInode::setAttrData`, `FileInode::incDecNumHardLinks`, and close/update methods. The implementation depends on `Program` to access `MetaStore` and its `GlobalInodeLockStore`.

## Integration Points

`MetaStore` uses the global store for non-inlined inodes and as the target when references move out of per-directory stores. `DirInode` uses a per-directory store for inlined inode objects. `MetaStoreRename` uses move begin/complete during remote rename. `GlobalInodeLockStore` blocks normal loads through `lookupFileInode`.

## Risks and Test Signals

The most important race is deletion of an inode still referenced through another store; `deleteUnreferencedInodeUnlocked` explicitly checks refcount to avoid use-after-free during rename/hardlink/open races. Non-inlined inodes found in directory stores are treated as in-use and cleaned up to restore global-store invariants. Tests should cover global lock rejection, bypass for internal state update, exclusive TID behavior, open failure release, last-writer detection, unlink in-use cases, remote move begin/complete, and stale inline flag recovery.
