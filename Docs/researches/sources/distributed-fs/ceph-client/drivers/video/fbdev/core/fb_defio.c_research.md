# sources/distributed-fs/ceph-client/drivers/video/fbdev/core/fb_defio.c

## Purpose

This file implements fbdev deferred I/O, allowing mmap writes to framebuffer memory to be collected as dirty page references and flushed to a driver callback after a delay or fsync/last-close. The complete 479-line source was read.

## Important APIs, Types, and Functions

Private state is `struct fb_deferred_io_state`, with a kref, open count, file mapping, lock, active `fb_info`, fixed pageref array, and dirty pageref list. Exported APIs include `fb_deferred_io_fsync()`, `fb_deferred_io_mmap()`, `fb_deferred_io_init()`, `fb_deferred_io_open()`, `fb_deferred_io_release()`, and `fb_deferred_io_cleanup()`. Internal flow uses `fb_deferred_io_fault()`, `fb_deferred_io_track_page()`, `fb_deferred_io_mkwrite()`, `fb_deferred_io_work()`, and pageref lookup/get/put helpers.

## Control Flow

Initialization allocates one pageref per framebuffer page, initializes delayed work, sets default delay to one second when unset, and stores state in `info->fbdefio_state`. Open records the file mapping and installs deferred I/O address-space ops. Mmap installs vm ops, marks VM flags, stores the state as `vm_private_data`, and takes module/state refs. Fault resolves a page from the driver callback, vmalloc buffer, or physical `smem_start`. Page-mkwrite records the touched page, locks it until the PTE is dirtied, schedules delayed work, and returns `VM_FAULT_LOCKED`. Workqueue processing write-protects dirty mappings under MMU, calls the driver's `deferred_io()` callback with the pageref list, and clears the list. Cleanup flushes work, detaches `info`, and drops the state ref.

## State and Persistence Behavior

State is entirely in memory: pageref array/list, delayed work, mapping pointer, open count, krefs, and framebuffer page references. Deferred writes persist only when the driver's callback copies or sends changed pages to backing hardware/storage. No file-backed persistence is implemented here.

## Dependencies and Integration Points

The file depends on mm fault/page-mkwrite APIs, rmap write-protection, page cache mapping ops, delayed work, vmalloc-to-page, optional driver `get_page()`, and the fbdev char-device open/release/fsync hooks. It is selected by `CONFIG_FB_DEFERRED_IO`.

## Risks and Edge Cases

Key risks are lifetime races between VMAs and device removal, mapping pointer replacement by multiple opens, O(n^2) sorted pageref insertion when `sort_pagereflist` is enabled, memory cost proportional to framebuffer pages, page reference handling for physical `smem_start`, and drivers failing to tolerate unsorted lists. Cleanup sets `info=NULL` under the state lock so later faults return `SIGBUS`, which is intentional but should be tested. `open_count` is protected by the fb_info lock rather than the defio mutex.

## Test Signals

Test mmap page faults, repeated writes to the same page, writes from multiple processes, delayed callback batching, fsync flushing, last-close flushing, cleanup during live VMA access, driver `get_page()` override, vmalloc and physical framebuffer backing, sorted versus unsorted pageref lists, MMU write-protection behavior, and lockdep/KASAN/KCSAN stress.
