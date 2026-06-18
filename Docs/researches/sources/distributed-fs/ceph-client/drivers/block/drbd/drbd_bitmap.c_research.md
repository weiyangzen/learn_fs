# sources/distributed-fs/ceph-client/drivers/block/drbd/drbd_bitmap.c

## Purpose

`drbd_bitmap.c` implements DRBD's in-memory and on-disk out-of-sync bitmap. One bitmap bit represents a 4 KiB block of replicated storage. The file handles bitmap allocation, resize, locking, bit mutation, counting, search, endian-stable transfer, dirty-page tracking, and asynchronous bitmap I/O to the DRBD metadata area.

## Important APIs, Types, and Data

- `struct drbd_bitmap` owns the page array, `bm_lock`, `bm_change`, bitmap page I/O wait queue, dirty/hint arrays, bit/word/page counts, capacity, set-bit count, flags, and lock debugging fields.
- Page-private bits encode page index and state: `BM_PAGE_IO_LOCK`, `BM_PAGE_IO_ERROR`, `BM_PAGE_NEED_WRITEOUT`, `BM_PAGE_LAZY_WRITEOUT`, and `BM_PAGE_HINT_WRITEOUT`.
- Public lock/lifecycle APIs: `drbd_bm_init()`, `drbd_bm_cleanup()`, `drbd_bm_lock()`, `drbd_bm_unlock()`, `drbd_bm_resize()`, and `drbd_bm_capacity()`.
- Public bitmap status APIs: `_drbd_bm_total_weight()`, `drbd_bm_total_weight()`, `drbd_bm_words()`, `drbd_bm_bits()`, `drbd_bm_find_next()`, `_drbd_bm_find_next()`, `_drbd_bm_find_next_zero()`, `drbd_bm_test_bit()`, `drbd_bm_count_bits()`, and `drbd_bm_e_weight()`.
- Public mutation APIs: `drbd_bm_merge_lel()`, `drbd_bm_get_lel()`, `drbd_bm_set_all()`, `drbd_bm_clear_all()`, `drbd_bm_set_bits()`, `drbd_bm_clear_bits()`, and `_drbd_bm_set_bits()`.
- I/O APIs: `drbd_bm_read()`, `drbd_bm_write()`, `drbd_bm_write_all()`, `drbd_bm_write_lazy()`, `drbd_bm_write_copy_pages()`, and `drbd_bm_write_hinted()`.
- AL integration APIs: `drbd_bm_reset_al_hints()` and `drbd_bm_mark_for_writeout()`.

## Control Flow

`drbd_bm_init()` allocates and initializes the bitmap object but not its pages. `drbd_bm_resize()` is called when device capacity changes. It serializes through `drbd_bm_lock()`, computes the number of bits and 64-bit-aligned words needed, verifies on-disk metadata has enough bitmap space when a local disk exists, reallocates the page-pointer array and pages, copies existing pages, initializes new ranges either set or clear, updates capacity/count metadata under `bm_lock`, clears surplus bits beyond capacity, frees truncated pages, recounts on shrink, and unlocks.

Bit operations map page-sized chunks with `kmap_atomic()`. `bm_change_bits_to()` and `__bm_change_bits_to()` update individual bit ranges, maintain `bm_set`, and mark pages either `NEED_WRITEOUT` when bits are set or `LAZY_WRITEOUT` when bits are cleared. `_drbd_bm_set_bits()` optimizes large set ranges by filling full words while still accounting for changed bits.

Find/count operations walk bitmap pages under `bm_lock` and use little-endian bit helpers. The bitmap is intentionally stored little endian in memory and on disk, which simplifies network transfer and cross-platform operation.

Bitmap I/O is centralized in `bm_rw()`. It creates a `drbd_bm_aio_ctx`, gets a local disk reference, records the context in `pending_bitmap_io`, submits one bio per selected bitmap page through `bm_page_io_async()`, waits for `in_flight` completion via `misc_wait`, handles I/O errors, recounts set bits after reads, and drops the context krefs.

`bm_page_io_async()` computes the metadata sector for the page, trims length for small external metadata areas, serializes per-page I/O with `BM_PAGE_IO_LOCK`, clears dirty/lazy state before submission so concurrent changes redirty the page, optionally copies the page for writeout that may race with ongoing bitmap mutation, builds a bio, and submits or fault-injects it. `drbd_bm_endio()` records errors, unlocks the page, frees copied pages, and completes the context.

Write variants select pages differently: normal write skips unchanged pages, write-all writes every page, lazy write uses copied pages and optionally stops at an upper page index, copy-pages writes changed pages via temporary pages, and hinted write writes only AL-marked pages that are still dirty.

## State and Persistence Behavior

The in-memory bitmap is authoritative while a local disk is attached. Dirty page-private flags track what must be written to metadata. The on-disk bitmap lives in the metadata area beginning at `md_offset + bm_offset` and ending before the AL or metadata end depending on internal/external layout.

`bm_set` caches the total number of out-of-sync bits. It is maintained incrementally on mutations and recounted after reads or shrink. Surplus bits outside device capacity are cleared for normal semantics; 32-bit padding alignment is explicitly handled for 32/64-bit interoperability.

Page I/O errors mark `BM_PAGE_IO_ERROR` and trigger DRBD metadata I/O error handling. Lazy writeout permits cleared bits to be deferred because remote bitmap exchange can reconstruct them if necessary; set bits are marked for stronger writeout.

## Dependencies and Integration Points

- DRBD core structs and metadata layout from `drbd_int.h`.
- Activity log integration in `drbd_actlog.c` through hinted bitmap writeout.
- Block layer bio APIs and the shared DRBD metadata bio set/page mempool.
- Linux bitmap, highmem, vmalloc/kvfree, waitqueue, spinlock, mutex, and kref APIs.
- DRBD fault injection for bitmap allocation and metadata read/write faults.
- Debugfs observes `pending_bitmap_io` via `drbd_debugfs.c`.

## Risks and Edge Cases

- Very large devices produce very large bitmaps; comments document limits, especially on 32-bit architectures.
- Bitmap resize must avoid deadlocks by using `GFP_NOIO` while DRBD I/O may be suspended.
- `bm_set` is protected by `bm_lock` but comments note inherent raciness for callers that do not hold broader synchronization.
- Page-private state combines index and flags; incorrect bit usage can corrupt both I/O state and page identity.
- `bm_rw()` relies on local disk references to keep bitmap and metadata devices stable during asynchronous I/O.
- Copy-pages writeout is necessary where bitmap changes may continue during writeback. Using normal writeback in those contexts can lose dirtying information.
- Metadata sector trimming for small external metadata devices must avoid reading/writing beyond valid bitmap space.

## Test Signals

- Resize tests for zero capacity, grow with new bits set/clear, shrink, metadata space too small, allocation failure injection, and 32-bit padding behavior.
- Bit operation tests for set, clear, large range set, count, find-next, extent weight, and surplus masking.
- Endian/interoperability tests for `drbd_bm_merge_lel()` and `drbd_bm_get_lel()`.
- Bitmap I/O tests for read, normal write, write-all, lazy write, copy-pages, hinted write, metadata I/O errors, and force-detach/timeouts.
- Stress tests with concurrent bit changes during copy-pages and normal I/O to confirm pages are redirtied or warnings trigger appropriately.
- Locking tests around `bm_change`, `bm_lock`, page I/O locks, and pending bitmap I/O list handling.
