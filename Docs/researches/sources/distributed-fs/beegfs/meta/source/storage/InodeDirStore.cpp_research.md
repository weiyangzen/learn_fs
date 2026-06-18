# sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.cpp

## Purpose

`InodeDirStore.cpp` implements the directory-inode cache/reference store for the metadata server. It loads `DirInode` objects on demand, reference-counts them, maintains a configurable reference cache, supports stat/setattr/remove operations, and invalidates mirrored directories after role or consistency changes.

## Important APIs and Functions

The constructor reads cache limits from config. `referenceDirInode` finds, creates, optionally force-loads, references, and cache-adds directory inodes. `releaseDir` and `releaseDirUnlocked` drop references and delete entries when no references remain. `removeDirInode` removes cache state, checks removability, and unlinks persistent directory metadata. `stat`, `setAttr`, `invalidateMirroredDirInodes`, `getSize`, `getCacheSize`, and `cacheSweepAsync` provide operational access.

Private helpers include `insertDirInodeUnlocked`, `isRemovableUnlocked`, `cacheAddUnlocked`, `cacheRemoveUnlocked`, `cacheRemoveAllUnlocked`, and `cacheSweepUnlocked`.

## Control Flow and State

`referenceDirInode` starts with a read lock, upgrades to write only if the directory is missing, and inserts a new `DirectoryReferencer` when needed. If `forceLoad` is true, it loads the inode after releasing the store lock and releases it again if disk load fails. Cache insertion takes an extra reference, so cached directories stay alive until swept or explicitly removed. `releaseDirUnlocked` refuses to delete a directory whose embedded file store still has references unless the app is terminating.

`stat` checks owner identity for loaded directories and falls back to static `DirInode::getStatData` when absent. `setAttr` either applies directly to a loaded non-exclusive directory or temporarily loads a stack `DirInode`.

## Persistence and Dependencies

Persistent operations delegate to `DirInode::loadFromFile`, `DirInode::unlinkStoredInode`, `DirInode::getStatData`, and `DirInode::setAttrData`. The store depends on `Program`, config, POSIX ACL support, threading guards, and `DirInode`.

## Integration Points

`MetaStore` owns `dirStore` and calls it for directory references, stat, setattr, removal, cache stats, and cache sweeps. `DirInode` embeds an `InodeFileStore`, so directory release must account for file references held through `MetaFileHandle`.

## Risks and Test Signals

Key risks are lock-order deadlocks, cache references masking removability, owner mismatch for mirrored/root directories, and deleting directories while child file references remain. Tests should cover reference/release balance, force-load failure cleanup, cache sweep thresholds, removing loaded/nonloaded directories, mirrored invalidation, and `releaseDir` error logging when fileStore is non-empty.
