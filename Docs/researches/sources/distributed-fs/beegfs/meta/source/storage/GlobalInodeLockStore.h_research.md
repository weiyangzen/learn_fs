# sources/distributed-fs/beegfs/meta/source/storage/GlobalInodeLockStore.h

## Purpose

`GlobalInodeLockStore.h` declares the global internal-operation inode lock store. The "lock" is represented by successful insertion into a process-wide map and a reference-counted `FileInode`, not by a kernel or POSIX file lock.

## Important APIs and Types

`LockOperationType` currently distinguishes `CHUNK_REBALANCING` and `FILE_STATE_UPDATE`. `GlobalInodeLockEntry` groups the inode referencer, operation type, and elapsed-time counter so parallel side maps cannot diverge. `GlobalInodeLockStore` exposes insert, release, lookup, referenced and unreferenced accessors, timeout update, full cleanup, operation-specific cleanup, and counters.

## Control Flow and State

The class owns `GlobalInodeLockMap inodes` and an `RWLock`. Private helpers centralize operation-string formatting, unlocked release, refcount increase/decrease, and timeout reset. The destructor calls `clearLockStore`, so all held inode references are deleted on store destruction.

## Persistence and Dependencies

The header depends on `FileInode`, `ObjectReferencer`, file event logging, and common storage errors. It has no durable state of its own, but it loads durable inode metadata and blocks regular load paths while entries are present.

## Integration Points

`MetaStore` contains one `GlobalInodeLockStore` and exposes it through `getInodeLockStore`. `InodeFileStore` consults it when `checkLockStore` is true. State update and chunk balancing code use operation types to avoid clearing each other's locks.

## Risks and Test Signals

Operation type must be threaded consistently through insert, release, timeout, and cleanup. Adding a new operation type requires extending `opTypeToString` and validating all callers. Tests should verify public counters, selective cleanup, destructor cleanup behavior, and interaction with regular `InodeFileStore` loads.
