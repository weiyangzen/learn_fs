## sources/distributed-fs/beegfs/meta/source/session/EntryLockStore.h

Purpose: defines key-to-lock storage for metadata entry locking. It avoids unbounded allocation churn by using fixed hash buckets and small per-bucket buffers of reusable lock descriptors.

Important APIs/types: `ValueLockHash<Value>` specializations hash strings, parent/name pairs, and hash-dir pairs. `ValueLockStore<Value, Lock, HashSize, BufferSize>` manages `ValueLock` descriptors containing a lock primitive, key value, bucket pointer, list iterator, and reference count. Type aliases define `ParentNameLockStore`, `FileIDLockStore`, `HashDirLockStore`, and their descriptor types. `EntryLockStore` exposes typed lock/unlock functions.

Control flow: `getLockFor` hashes the key, locks the bucket mutex, searches active descriptors, either reuses a buffered descriptor or allocates a new one, increments references, and returns it. `putLock` decrements references and moves unused descriptors into the bucket buffer or deletes them when the buffer is full.

State and persistence behavior: all state is volatile. The active list and buffer list per bucket determine descriptor lifetime and allocation patterns.

Dependencies and integration points: integrates with BeeGFS `Mutex`, `RWLock`, `LogContext`, and the RAII wrappers in `EntryLock.h`. Hash choices are tuned for metadata entry IDs and inode/dentry hash-dir fragments.

Risks: active descriptor lookup is linear within a bucket, so pathological hash concentration can increase lock acquisition time. The parent/name hash specialization signature accepts `std::pair<const std::string&, const std::string&>` while the specialization type is `std::pair<std::string, std::string>`, relying on compatible invocation patterns. `ValueLock` objects are manually allocated and deleted.

Test signals: bucket buffer saturation, repeated same-key acquisition reference counts, pair-hash consistency, concurrent `getLockFor`/`putLock`, and no descriptor reuse while references remain are key tests.
