## sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.cpp

Purpose: implements typed lock acquisition and release for metadata entries. It maps high-level lock requests to `Mutex` or `RWLock` primitives held in `ValueLockStore` buckets.

Important functions: `lock(parentID,name)` gets a parent/name mutex descriptor and locks it. `lock(fileID, writeLock)` gets an `RWLock` descriptor and takes a read or write lock. `lock(hashDir)` gets and locks a hash-directory mutex. The three `unlock` overloads unlock the primitive and then return the descriptor to its store.

Control flow: each lock method first obtains a reference-counted descriptor from the appropriate `ValueLockStore`, then locks the underlying primitive before returning. Unlock reverses the order: release primitive first, decrement descriptor reference second.

State and persistence behavior: lock descriptors are transient in-memory state. Reference counts and per-bucket buffers live in `EntryLockStore`.

Dependencies and integration points: used by `EntryLock.h` RAII wrappers and metadata mirrored message lock methods. Depends on `Mutex` and `RWLock` from BeeGFS common threading.

Risks: callers must use the matching `unlock` overload for the descriptor type; RAII wrappers help enforce this. If a thread blocks while taking the primitive after descriptor acquisition, the descriptor stays referenced and cannot be recycled.

Test signals: concurrent acquisition/release by same and different keys, read/write exclusion for file IDs, descriptor reuse after buffer return, and hash collision behavior should be tested.
