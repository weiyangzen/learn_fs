# sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.cpp

## Purpose

`GlobalInodeLockStore.cpp` implements a process-wide map of file inodes reserved for internal metadata operations. It prevents normal metadata paths from loading or mutating the same inode while operations such as chunk rebalancing or file-state updates require exclusive coordination.

## Important APIs and Functions

`opTypeToString` formats `LockOperationType`. `insertFileInode` loads an inode from `EntryInfo`, inserts a `GlobalInodeLockEntry`, validates operation-type compatibility, optionally increments the reference count, and emits file events. `releaseFileInode` and `releaseFileInodeUnlocked` validate the operation type before releasing references and deleting the entry at refcount zero. Lookup and accessor methods include `lookupFileInode`, `getFileInode`, and `getFileInodeUnreferenced`. Maintenance APIs include `updateInodeLockTimesteps`, `clearLockStore`, `clearLockStoreByOpType`, and operation-filtered counters.

## Control Flow and State

All map mutation is guarded by `rwlock` in write mode. Inserts are keyed by entry ID. Existing entries are accepted only when the requested operation type matches the stored type; different operation types receive `FhgfsOpsErr_INODELOCKED`. New entries call `FileInode::createFromEntryInfo`, wrap the object in an `ObjectReferencer`, and initialize elapsed time to zero. Reference increments are explicit, and `getFileInode` resets the timeout counter when a new reference is taken.

Timeout cleanup iterates only entries of the requested operation type, adds elapsed seconds, and force releases entries past the configured max. Clear operations delete referencers and entries directly.

## Persistence and Dependencies

The store itself is memory-only, but it holds fully loaded `FileInode` objects whose persistence APIs may be called by the owning operation. It depends on `Program::getApp`, `FileEventLogger`, `FileInode`, `EntryInfo`, and `RWLockGuard`. Event logging uses `makeEventContext` and records `INODE_LOCKED` style events when callers provide a `FileEvent`.

## Integration Points

`InodeFileStore::referenceFileInodeUnlocked` checks this store before loading from disk in normal paths. `MetaStore::setFileState` inserts with `LockOperationType::FILE_STATE_UPDATE` and bypasses normal lock-store checks while referencing the locked inode. Chunk balancing uses the chunk-rebalancing operation type.

## Risks and Test Signals

The main risk is leaked global locks on error paths; the code logs severe messages because such leaks can block inode access until metadata service restart. Operation-type mismatches protect unrelated internal operations but require every release to pass the same type used at insert. Timeout release may leave orphaned chunks and logs fsck guidance. Tests should cover same-op refcount sharing, different-op rejection, release mismatch failure, timeout cleanup by operation type, event logging on insert, and cleanup when inode creation fails.
