# sources/distributed-fs/beegfs/meta/source/storage/InodeDirStore.h

## Purpose

`InodeDirStore.h` declares the metadata server store for directory inodes. It is the directory counterpart to `InodeFileStore`, but uses `AtomicObjectReferencer` and an additional cache map because directory references are frequent and many client operations only need lightweight locking.

## Important APIs and Types

`DirectoryReferencer` is an `AtomicObjectReferencer<DirInode*>`. `DirectoryMap` stores owned directory referencers keyed by directory ID. `DirCacheMap` stores cached raw `DirInode*` values keyed by the same ID. Public APIs reference/release directories, test in-store state, remove persistent directory inodes, stat/setattr directories, invalidate mirrored directories, inspect reference/cache sizes, and trigger async cache sweeping.

## Control Flow and State

The class owns `dirs`, synchronous and asynchronous cache limits, a random generator for sweep starting points, `refCache`, and `rwlock`. Copy and move are explicitly deleted to keep referencer and cache ownership stable. The destructor clears cache references and all directory referencers.

## Persistence and Dependencies

The header depends on common storage and threading types plus `DirInode` forward declaration. Persistent disk behavior is delegated to `DirInode`, but this store determines when objects are loaded, kept cached, or removed.

## Integration Points

`MetaStore` is a friend and owns an instance. `DirInode` is also a friend, allowing tight integration with per-directory file stores and directory metadata internals.

## Risks and Test Signals

The extra cache reference means tests should verify release counts when cache entries are added and removed. Any change to cache limits or sweep strategy can affect memory pressure and latency. Tests should confirm destructor cleanup, disabled cache behavior, sync and async sweep behavior, and directory removability when loaded, cached, exclusive, or non-empty.
