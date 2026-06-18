# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/indexer/volume.h

## Purpose
`volume.h` defines the UDS volume interface and the internal cache/read-queue structures shared with `volume.c`. It documents that a volume is both the persistent chapter region and the code object that manages storage I/O.

## Important APIs, Types, and Functions
`enum index_lookup_mode` distinguishes normal lookup from rebuild lookup. `struct queued_read` represents one pending physical page read plus linked waiting requests. `struct cached_page` holds a `dm_buffer`, physical page number, LRU timestamp, and decoded `delta_index_page`. `struct page_cache` owns cache arrays, physical-page-to-cache/read-queue index, pending-search counters, read-queue cursors, and an LRU clock. `struct volume` owns geometry, bufio client, nonce, sorter, sparse cache, page cache, index page map, reader-thread synchronization, lookup mode, and reserved buffer count. The prototypes expose construction, teardown, storage replacement, search, write, prefetch, and page read helpers.

## Control Flow
The header has no runtime logic, but it defines the contracts used by index search and rebuild code: callers create a `volume`, search page cache or record pages, forget overwritten chapters, write closed chapters, prefetch chapters, and read index/record pages by chapter/page.

## State and Persistence Behavior
The structs separate persistent volume data from volatile cache state. `volume->client` is the handle to durable chapter storage; `page_cache` and `sparse_cache` are only runtime accelerators. Read-queue indices are circular buffer cursors, and `search_pending_counter` is cacheline-aligned to avoid cross-zone contention.

## Dependencies and Integration Points
The header includes Linux atomic/cache/dm-bufio types plus UDS geometry, layout, indexer, index page map, radix sort, sparse cache, and VDO assertion/thread utilities. It is included by volume implementation and index/rebuild code that needs volume operations.

## Risks and Edge Cases
Because several internal structures are visible, callers must still respect the intended ownership: direct mutation of cache fields would bypass locking and barriers. Cache sizing uses `u16` slots and flags, so callers must honor implementation limits. `lookup_mode` changes corruption handling semantics and should be controlled by rebuild code only.

## Test Signals
Compile coverage should catch signature drift across index modules. Runtime signals come from successful volume construction/destruction, reader-thread startup, cache size accounting, normal and rebuild lookup paths, and storage replacement with no stale `dm_buffer` references.
