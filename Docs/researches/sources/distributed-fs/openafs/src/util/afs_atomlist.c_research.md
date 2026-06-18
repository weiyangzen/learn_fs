
# sources/distributed-fs/openafs/src/util/afs_atomlist.c

Purpose: `afs_atomlist.c` implements a block-backed fixed-size allocator for small objects. It reduces allocator fragmentation by allocating large blocks, splitting them into aligned atoms, and maintaining a free list.

Important APIs and functions: `afs_atomlist_create()` validates and aligns atom/block sizes, stores caller-provided allocation hooks, and initializes lists. `afs_atomlist_get()` allocates a new block when the free list is empty, chains the block into `block_head`, threads its atoms into `atom_head`, and returns one atom. `afs_atomlist_put()` returns an atom to the free list. `afs_atomlist_destroy()` frees every allocated block and the allocator object.

Control flow: block layout stores the next-block pointer after all usable atoms, using leftover block space when possible. Atom size is rounded up to pointer size and pointer alignment. If block size cannot hold at least one atom plus a next-block pointer, creation fails.

State and persistence: allocator state is in `struct afs_atomlist`: atom size, block size, atoms per block, allocation hooks, atom free-list head, and block list head. No persistent external state exists.

Dependencies and integration: used by `afs_lhash.c` to allocate bucket records. Caller provides memory allocation functions and locking if needed.

Risks: no internal locking, no validation that returned atoms belong to this allocator, and no double-free detection. Allocation failure during `get` returns NULL. Test signals should cover alignment, minimal block-size rejection, block growth, atom reuse after put, destruction with outstanding atoms, and custom allocator failure paths.
