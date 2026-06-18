## sources/distributed-fs/beegfs/meta/source/session/EntryLock.h

Purpose: RAII wrappers around `EntryLockStore` locks for file IDs, parent/name pairs, and hash-directory fragments. These wrappers make mirrored-message and metadata operation locking exception/return-path safe.

Important APIs/types: `UniqueEntryLockBase<LockDataT>` owns an `EntryLockStore*` and a lock descriptor pointer and unlocks in its destructor. It is move-only and supports `swap`. `FileIDLock`, `ParentNameLock`, and `HashDirLock` specialize the base for `FileIDLockData`, `ParentNameLockData`, and `HashDirLockData`.

Control flow: constructors call `entryLockStore->lock(...)` and retain the returned descriptor. Destruction calls `entryLockStore->unlock(lockData)` if a descriptor is held. Move construction/assignment transfers ownership by swapping pointers.

State and persistence behavior: state is in-memory locking only. No session or metadata state is serialized here.

Dependencies and integration points: includes `EntryLockStore.h`. Message handlers in `net/message/...` return these types from `lock(EntryLockStore&)` methods to synchronize mirrored operations and local metadata mutation.

Risks: the base assumes `entryLockStore` remains alive longer than all wrappers. The inheritance is private for concrete classes, which is fine for RAII use but means callers only interact through construction/destruction. Default-constructed locks are empty and safe.

Test signals: tests should cover move construction/assignment, destructor unlock exactly once, empty lock destruction, and lock ordering in message handlers that return tuples of these lock types.
