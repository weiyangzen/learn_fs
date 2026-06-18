# sources/distributed-fs/openafs/src/afs/afs_axscache.c

Purpose: Provides allocation, lookup assistance, removal, list-free, and shutdown logic for small per-vnode access-cache entries (`struct axscache`) used to memoize access rights by user id.

Important APIs and functions: `afs_SlowFindAxs` scans a linked list after the fast head check in `afs_FindAxs` misses and moves a found entry to the front. `axs_Alloc` allocates entries from a freelist, bulk-allocating `struct xfreelist` slabs. `afs_RemoveAxs` removes one entry from a parent list and returns it to the freelist. `afs_FreeAllAxs` prepends a whole list to the freelist. `shutdown_xscache` releases all slab allocations.

Control flow: Allocation takes `afs_xaxs`, pops `afs_axsfreelist` when possible, otherwise allocates a slab, initializes each entry with sentinel uid/access values, chains the rest onto the freelist, and returns the first entry. Lookups walk two nodes per loop and use the `axs_Front` macro for LRU-style promotion. Frees take only the global freelist lock; list lookup/removal relies on the caller holding the parent object's lock.

State and persistence: Maintains process/kernel-memory globals `afs_axsfreelist`, `xfreemallocs`, `afs_xaxscnt`, and lock `afs_xaxs`. There is no disk persistence; shutdown frees all slabs and clears globals.

Dependencies and integration points: Depends on allocation primitives, OpenAFS lock macros, and the `struct axscache` contract from `afs_axscache.h`. The data is embedded by higher-level cache objects that own the access-cache list and are responsible for parent-level synchronization.

Risks: The package is optimized for lookup speed and assumes correct external locking around list membership. The remove loop is especially fragile: after checking `j == axsp`, the next unrolled branch assigns `i = j->next` and frees `axsp` without comparing `i` to `axsp`, which is a potential wrong-entry unlink/free path if exercised. Freelist entries are not scrubbed on free beyond later allocation initialization.

Test signals: Allocate more than one slab, find head and non-head entries, verify front promotion, remove head/middle/tail/missing entries, free whole lists with odd/even lengths, run concurrent allocation/free under caller locking assumptions, and validate shutdown releases every slab.
