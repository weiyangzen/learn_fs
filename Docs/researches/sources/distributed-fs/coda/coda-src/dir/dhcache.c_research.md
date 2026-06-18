# sources/distributed-fs/coda/coda-src/dir/dhcache.c

## Purpose
Directory-handle cache keyed by `DirInode`, used as a child of the Coda vnode cache. It maps persistent/inode directory pages to mutable `DirHandle` copies and tracks references, dirty state, and copy-on-write handoff.

## APIs, Types, and Functions
Defines internal `struct DCEntry` with hash/list links, counts, `DirHandle`, primary `PDirInode`, and COW inode. Public routines include `DC_HashInit()`, `DC_Get()`, `DC_Put()`, `DC_New()`, `DC_Rehash()`, `DC_Drop()`, `DC_Count()`, `DC_SetCount()`, `DC_Refcount()`, `DC_SetRefcount()`, `DC_DC2DH()`, `DC_DH2DC()`, `DC_DC2DI()`, `DC_SetDI()`, `DC_SetDirh()`, `DC_SetCowpdi()`, `DC_Cowpdi()`, `DC_SetDirty()`, and `DC_Dirty()`. Internal helpers are `dc_Grow()`, `dc_GetFree()`, and `DC_Hash()`.

## Control Flow, State, and Persistence
`DC_HashInit()` initializes the global lock, hash buckets, free list, and new-list. `DC_Get()` looks up by inode, increments `dc_count`, removes first users from the free list, and refreshes flushed handle data with `DI_DiToDh()`; misses allocate a free entry and hash it. `DC_Put()` returns clean zero-user entries to the free list. `DC_New()` creates dirty uncommitted entries on `dnewlist`, and `DC_Rehash()` moves them to the hash table after inode creation.

## Dependencies and Integration
Depends on LWP locking, `dllist`, `DirInode` conversion, and `DH_FreeData()`. It integrates vnode lifetime with directory copy-on-write and commit paths.

## Risks and Test Signals
Risks include pointer-derived hash distribution, global lock granularity, assertions that entries are clean when freed, no freelist destruction path, possible list misuse if counts underflow, and cache data refresh depending on valid `DirInode` pages. Test signals are repeated get/put cycles, cache hit refcounts, COW commit rehashing, dirty-entry exclusion from freelist, and leak checks around `DC_Drop()`.
