
# sources/distributed-fs/openafs/src/util/afs_atomlist.h

Purpose: `afs_atomlist.h` declares the fixed-size atom allocator abstraction used by utility code needing low-fragmentation allocation.

Important APIs: opaque `afs_atomlist`; `afs_atomlist_create(atom_size, block_size, allocate, deallocate)`; `afs_atomlist_destroy()`; `afs_atomlist_get()`; and `afs_atomlist_put()`.

Control flow and integration: the header documents caller-supplied allocation hooks and states that destroying the allocator frees all blocks, including atoms not returned individually. It explicitly assigns locking responsibility to callers.

State and persistence: the type is opaque, so callers cannot access block/free-list internals. No persistent state beyond process memory.

Risks and test signals: callers must not return foreign or already-returned atoms. Tests should verify opaque ABI usage, allocation-hook invocation counts, and behavior under failed allocation.
