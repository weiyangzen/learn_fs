# sources/distributed-fs/ceph-client/drivers/android/binder_alloc.h

## Purpose
`binder_alloc.h` declares the Binder allocator data model and public C API. It is the contract between the Binder core and `binder_alloc.c` for transaction buffer allocation, mmap initialization, freeing, copying, debug reporting, shrinker setup, and KUnit-only introspection.

## Important APIs, Types, And Functions
`struct binder_buffer` describes one transaction buffer with list/rb-tree membership, free/clear/user-free/async/spam flags, debug ID, transaction/node pointers, sizes, user address, and pid. `struct binder_shrinker_mdata` stores per-page LRU metadata and the owning allocator/page index. `struct binder_alloc` stores allocator-wide mutex, mm, VMA start, buffer lists and rb trees, free async space, page array, LRU, buffer size, pid, pages high watermark, mapped flag, and spam state. Public prototypes cover allocation/free, mmap, deferred release, vma close, shrinker lifecycle, debug printing, allocated count, user/kernel copy helpers, and `binder_alloc_get_free_async_space`.

## Control Flow
The header has only inline helpers and declarations. `page_to_lru` converts a page's private metadata to its LRU node. `binder_alloc_get_free_async_space` locks the allocator mutex and returns the async-space counter. Callers follow the lifecycle: `binder_alloc_init`, `binder_alloc_mmap_handler`, repeated `binder_alloc_new_buf` and free/copy operations, `binder_alloc_vma_close`, then `binder_alloc_deferred_release`.

## State And Persistence
The header defines the persistent allocator state held per Binder process and per buffer. `mapped` is specifically documented as a lifetime gate: each Binder instance gets a single mapping. The page array and LRU metadata persist until deferred release or shrinker reclaim.

## Dependencies
It includes Linux rb-tree, list, mm, rtmutex, vmalloc, slab, list_lru, and Binder UAPI headers. It forward-declares `struct binder_transaction` and exposes KUnit-only helpers when `CONFIG_KUNIT` is enabled.

## Integration Points
`binder_internal.h` embeds `struct binder_alloc` in `struct binder_proc`; Binder transaction code uses `struct binder_buffer`; binderfs/debugfs reporting can call print helpers; KUnit tests include this header directly to verify internal allocation behavior.

## Risks
Because this header exposes struct layouts, any field change is cross-module ABI inside the kernel driver. Bitfield flags in `binder_buffer` control security-sensitive free and zeroing behavior. The inline async-space accessor assumes the mutex is sufficient and should not be used in interrupt contexts. `page_to_lru` trusts `page_private` to contain valid Binder shrinker metadata.

## Test Signals
Compile all Binder objects and KUnit tests after layout changes, run allocator KUnit, verify debugfs output still compiles, test async-space queries under allocation/free churn, and use sparse/lockdep to catch misuse of exposed structures.
