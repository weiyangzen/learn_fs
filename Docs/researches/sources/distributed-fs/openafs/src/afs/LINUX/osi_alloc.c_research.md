# sources/distributed-fs/openafs/src/afs/LINUX/osi_alloc.c

## Purpose
This file implements OpenAFS Linux kernel memory allocation wrappers. It chooses `kmalloc` for small allocations and `vmalloc` for larger ones, tracks every returned allocation in an OpenAFS atom-list/hash-table registry, supports global cleanup at module shutdown, and provides optional fixed-size small/large private allocation spaces.

## Important APIs, types, and functions
- `struct osi_linux_mem` stores the original allocation pointer with low-bit allocation type tags.
- `osi_linux_alloc(size, drop_glock)` allocates zeroed memory, lazily initializes tracking structures, records the allocation, and returns the untagged address.
- `osi_linux_free(addr)` removes a tracked allocation from the hash table and frees it with the matching kernel free routine.
- `osi_linux_free_afs_memory()` frees all outstanding tracked chunks and destroys the atom list and hash table.
- `osi_linux_verify_alloced_memory()` iterates tracked chunks and verifies tag sanity/counts.
- `linux_alloc`, `linux_free`, `hash_chunk`, `hash_free`, and `hash_verify` are static helpers for allocation, deallocation, hashing, cleanup, and diagnostics.
- Optional `osi_AllocLargeSpace`, `osi_AllocSmallSpace`, `osi_FreeLargeSpace`, and `osi_FreeSmallSpace` wrap fixed-size `kmalloc`/`kfree` when `AFS_PRIVATE_OSI_ALLOCSPACES` is enabled.

## Control flow and behavior
`osi_linux_alloc` first calls `linux_alloc`, which retries up to ten times. Allocations at or below `PAGE_SIZE` use `kmalloc(GFP_NOFS)` and larger allocations use `vmalloc`; large allocations assert that either the global lock can be dropped or is not held, then temporarily releases `AFS_GLOCK` around `vmalloc` and retry sleeps when requested. Successful allocations are zeroed and tagged in the low two pointer bits as `KM_TYPE` or `VM_TYPE`. Under `afs_linux_alloc_sem`, the public allocator initializes the atom pool/hash table on first use, obtains a tracking node, records the tagged pointer, and enters it into `lh_mem_htab`.

Freeing constructs a lookup key from the untagged address, removes the tracking node, frees the tagged pointer via `linux_free`, returns the tracking node to the atom list, and decrements current allocation counters. Whole-module cleanup iterates the hash table with `hash_free`, then destroys both registry structures and clears `allocator_init`.

## State and persistence
The persistent module state is the allocator registry: `al_mem_pool`, `lh_mem_htab`, `allocator_init`, `afs_linux_cur_allocs`, `afs_linux_total_allocs`, and `afs_linux_hash_verify_count`. Memory survives until individually freed or until `osi_linux_free_afs_memory` runs during module shutdown. There is no disk persistence.

## Dependencies and integration points
The implementation uses Linux `kmalloc`, `kfree`, `vmalloc`, `vfree`, scheduler sleep primitives, and OpenAFS `afs_atomlist`/`afs_lhash` utilities. It is invoked by broader AFS kernel code through prototypes in `osi_prototypes.h` and cleaned from module/PAG-manager shutdown paths.

## Risks
The low-bit pointer tagging assumes kernel allocation alignment and comments mention 32-bit pointers, although the code casts through `unsigned long`. Any untracked pointer passed to `osi_linux_free` panics. Initialization failure after a successful raw allocation is carefully freed but could leak the atom list if hash creation fails before a later cleanup path. `osi_linux_verify_alloced_memory` computes a difference with unsigned counters, so mismatch diagnostics may underflow. Sleeping and dropping `AFS_GLOCK` around `vmalloc` are necessary but sensitive to callers' lock expectations.

## Test signals
Exercise small and large allocation/free cycles, allocation failure injection, shutdown cleanup with outstanding allocations, double/untracked free panic behavior, verify-count diagnostics, and builds with `AFS_PRIVATE_OSI_ALLOCSPACES`. Locking tests should cover calls with and without `AFS_GLOCK` and `drop_glock`.
