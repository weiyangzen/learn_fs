# sources/distributed-fs/ceph-client/drivers/android/binder_alloc.c

## Purpose
`binder_alloc.c` implements the classic C Binder per-process transaction buffer allocator. It manages the mmapped Binder buffer address space, best-fit buffer allocation, free-buffer coalescing, page installation into the target userspace VMA, LRU-based page reclamation, buffer zeroing, async-space accounting, oneway spam detection, debug output, and copy helpers for Binder payload data.

## Important APIs, Types, And Functions
Public functions include `binder_alloc_init`, `binder_alloc_shrinker_init`, `binder_alloc_shrinker_exit`, `binder_alloc_mmap_handler`, `binder_alloc_new_buf`, `binder_alloc_prepare_to_free`, `binder_alloc_free_buf`, `binder_alloc_deferred_release`, `binder_alloc_vma_close`, `binder_alloc_get_allocated_count`, `binder_alloc_print_allocated`, `binder_alloc_print_pages`, `binder_alloc_copy_user_to_buffer`, `binder_alloc_copy_to_buffer`, `binder_alloc_copy_from_buffer`, and the shrinker callback `binder_alloc_free_page`. Important internals include free/allocated rb-tree insertion, page install helpers, `sanitized_size`, `check_buffer`, async spam debugging, and LRU add/delete helpers.

## Control Flow
`binder_alloc_mmap_handler` validates a single mapping, caps it at 4 MiB, allocates the page array and initial free buffer, initializes async space to half the buffer, and marks the allocator mapped with release semantics. `binder_alloc_new_buf` validates mapping and size, preallocates a split buffer node, selects a best-fit free buffer under `alloc->mutex`, updates rb trees and async accounting, then installs missing pages into the remote mm. `binder_alloc_free_buf` optionally clears sensitive buffers, then coalesces adjacent free buffers and returns fully unused pages to the LRU. The shrinker walks the global `binder_freelist`, isolates pages, clears `alloc->pages`, zaps user mappings, and frees pages under careful mm/VMA/allocator locking.

## State And Persistence
Persistent state lives in `struct binder_alloc`: mm reference, mmap base, buffer list, free and allocated rb trees, free async byte count, installed page array, global or test LRU, buffer size, high watermark, mapped flag, and spam-detection flag. `struct binder_buffer` records each allocation's user address, sizes, flags, transaction/node pointers, and pid attribution. Pages persist until reclaimed by the shrinker or deferred release.

## Dependencies
The allocator depends on Linux mm APIs (`vm_insert_page`, `get_user_pages_remote`, VMA locking, `zap_vma_range`), rb trees, list LRU, shrinkers, highmem copy helpers, uaccess, module parameters, and `binder_trace.h`. KUnit-only exports are guarded through `VISIBLE_IF_KUNIT` and `EXPORT_SYMBOL_IF_KUNIT`.

## Integration Points
Binder process open/mmap initializes this allocator; transaction creation calls `binder_alloc_new_buf`; user `BC_FREE_BUFFER` flows call prepare/free; transaction delivery and object translation use copy helpers; debugfs/binderfs use print functions; memory pressure invokes the shrinker. The Rust Binder allocation wrapper likely maps onto the same concepts or symbols in this tree.

## Risks
This file is concurrency and lifetime sensitive. Page installation races are handled with release/acquire stores and `-EBUSY` lookup, while VMA close races are handled through `mapped`. Buffer coalescing must account for pages shared by adjacent buffers or pages can be reclaimed while still active. `check_buffer` is the boundary against invalid kernel copies. Shrinker lock ordering and VMA lifetime are the highest runtime-risk areas, and build coverage should catch API drift in mm, shrinker, and KUnit-export helpers.

## Test Signals
Run `binder_alloc` KUnit, especially exhaustive allocation/free/page-LRU cases; test mmap single-use behavior, invalid size overflow, async allocation exhaustion and spam detection, `TF_CLEAR_BUF` zeroing, shrinker reclaim under memory pressure, VMA close races, fd/object payload copy bounds, and debugfs page/buffer accounting. Build checks should catch the duplicate-source anomalies noted above.
