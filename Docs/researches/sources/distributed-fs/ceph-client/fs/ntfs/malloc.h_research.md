# sources/distributed-fs/ceph-client/fs/ntfs/malloc.h

## Purpose
`malloc.h` provides NTFS-specific memory allocation helpers that allocate in page-sized units and use NOFS allocation semantics for filesystem paths. It gives older NTFS code a small abstraction over `kmalloc`, `__vmalloc`, and `kvfree`.

## Important APIs, Types, and Functions
`__ntfs_malloc(size, gfp_mask)` allocates at least one page for small requests via `kmalloc(PAGE_SIZE, ...)` and larger requests via `__vmalloc()` if the request is smaller than total RAM pages. `ntfs_malloc_nofs(size)` adds `GFP_NOFS | __GFP_HIGHMEM`. `ntfs_malloc_nofs_nofail(size)` adds `__GFP_NOFAIL`. `ntfs_free(addr)` releases either allocation form through `kvfree()`.

## Control Flow and State
The allocation flow branches only on `size <= PAGE_SIZE`. Small nonzero allocations are rounded to a full page and use `kmalloc` with highmem stripped; larger allocations use vmalloc. There is no persistent state.

## State and Persistence Behavior
No filesystem metadata is changed. The persistence relevance is indirect: NOFS allocation avoids recursive filesystem reclaim while NTFS metadata paths hold locks or manipulate on-disk structures.

## Dependencies and Integration Points
It includes Linux `vmalloc.h`, `slab.h`, and `highmem.h`. It is intended for NTFS code paths that need page-multiple buffers and a common free function regardless of kmalloc/vmalloc backing.

## Risks
Small allocations always consume a full page, so using this helper for many tiny objects can waste memory. `BUG_ON(!size)` makes zero-size calls fatal. `ntfs_malloc_nofs_nofail()` can sleep indefinitely under memory pressure. The large allocation guard compares page count to `totalram_pages()` but does not guarantee practical vmalloc availability.

## Test Signals
Signals include compile coverage for callers, allocation-failure fault injection for non-nofail users, zero-size misuse detection in debug testing, and kmemleak/KASAN coverage that `ntfs_free()` correctly pairs with both allocation branches.
