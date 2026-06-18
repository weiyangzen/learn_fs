# sources/distributed-fs/coda/coda-src/vol/volhash.h

Purpose: declares the volume-id hash table abstraction used as the RVM volume index cache.

Important types/APIs: `vhashtab` extends `ohashtab` with a name, count, simple lock marker, add/remove/find/print methods. `vhash_iterator` wraps `ohashtab_iterator`. `hashent` stores `VolumeId` and recoverable storage index. Public C-style functions are `HashInsert`, `HashLookup`, and `HashDelete`.

Control flow/state: callers do not own the table directly; `InitVolTable` is a friend that allocates the global implementation. Hash entries are intrusive `olink` nodes.

Dependencies/integration: depends on Unix headers, `stdint`, `ohash`, `olist`, and Coda inconsistency/volume types. Risks include no exported `InitVolTable` declaration in this header, friend declaration typo for `vhashtab_iterator`, and lock methods that do not enforce mutual exclusion. Test signals: compile users, table initialization path in `VInitVolumePackage`, and hash operations around volume creation/deletion.
