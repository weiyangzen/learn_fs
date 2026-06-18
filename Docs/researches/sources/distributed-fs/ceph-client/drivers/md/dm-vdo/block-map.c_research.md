# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.c

## Purpose

`block-map.c` implements VDO's logical-to-physical block map. It combines a per-logical-zone leaf-page cache with an in-memory forest of radix trees that point to allocated block-map pages. The file is responsible for finding or allocating the block-map slot for a logical block, loading and writing block-map pages, tracking dirty pages by recovery-journal era, traversing the forest for rebuild/growth work, draining/resuming zones, and reporting cache statistics.

## Important APIs, Types, And Functions

- `UNMAPPED_BLOCK_MAP_ENTRY`: canonical on-disk entry for an unmapped logical block.
- Page-cache helpers: `vdo_get_page`, `vdo_release_page_completion`, `vdo_request_page_write`, `vdo_get_cached_page`, `vdo_invalidate_page_cache`, and `vdo_get_block_map_statistics`.
- Tree lookup/allocation: `vdo_find_block_map_slot`, `vdo_find_block_map_page_pbn`, `load_block_map_page`, `allocate_block_map_page`, and `finish_block_map_allocation`.
- Mapping access: `vdo_get_mapped_block`, `vdo_put_mapped_block`, `vdo_update_block_map_page`, and `set_mapped_location`.
- Forest lifecycle: `vdo_decode_block_map`, `vdo_record_block_map`, `vdo_free_block_map`, `make_forest`, `replace_forest`, `vdo_prepare_to_grow_block_map`, `vdo_grow_block_map`, and `vdo_abandon_block_map_growth`.
- Persistence scheduling: `vdo_initialize_block_map_from_journal`, `vdo_advance_block_map_era`, `add_to_dirty_lists`, `write_expired_elements`, `enqueue_page`, and `write_page`.
- Admin operations: `vdo_drain_block_map`, `vdo_resume_block_map`, zone `admin_state`, and the block-map `action_manager`.

## Control Flow

The page-cache path starts in `vdo_get_page`. It initializes a `vdo_page_completion`, checks read-only restrictions for writable requests, and then either returns a valid cached page, waits behind an incoming/outgoing page, loads the page into a free slot, or requests eviction of an LRU page. Dirty evictions are written only after `save_pages` issues a flush so recovery-journal entries reach stable storage before the block-map pages that depend on them. Completion paths validate page headers with the map nonce and PBN, format invalid pages as empty pages when appropriate, distribute the page to waiters, and maintain busy counts until callers release the page.

The tree lookup path starts in `vdo_find_block_map_slot` after a `data_vio` owns its LBN lock. It computes the root index and leaf slot, walks already loaded in-memory tree pages from the root toward the leaf, validates tree entries, and either finishes with the leaf page PBN or loads/allocates the missing interior/leaf page. `loading_pages` serializes concurrent loads or allocations by a packed `page_descriptor`; waiters resume after the owner finishes.

Allocation of missing block-map pages uses normal VDO block allocation, recovery-journal insertion, reference-count update to `MAXIMUM_REFERENCES`, and a block-map tree update. `finish_block_map_allocation` records the new child PBN in the parent tree page, formats newly allocated interior pages in memory, releases the page lock, wakes waiters, and continues descending until the final leaf slot is known.

Mapping reads and writes are layered on top of slot lookup. `vdo_get_mapped_block` treats an unallocated leaf page as unmapped, otherwise fetches the leaf page read-only and decodes the slot. `vdo_put_mapped_block` fetches the page writable, packs `data_vio->new_mapped`, transfers the recovery-journal lock to the page, marks the page dirty, and places it on dirty-era lists.

Forest traversal creates one cursor per root, uses a pooled metadata VIO per cursor to load pages, calls a supplied callback for allocated non-leaf PBNs, removes invalid or out-of-bound entries, and finishes the parent completion after all roots drain. Growth prepares a new segmented forest, then replaces the active forest during a suspended admin operation.

## State And Persistence Behavior

Persistent state is the on-disk block-map tree and block-map page entries. Each dirty page records the earliest recovery-journal sequence that has uncommitted changes. The code acquires and releases recovery-journal block references so journal blocks needed to replay dirty map updates are not reaped before the corresponding map page reaches disk. Page writes use initialized-header handling for torn-write protection and use preflush when the page is the active flusher.

In-memory state includes per-zone `loading_pages`, `active_lookups`, dirty-era lists, dirty generation counters, a VIO pool for metadata reads/writes, and the leaf-page cache (`page_info` state, LRU, free, outgoing, wait queues, busy counters, and statistics). Cache statistics are updated on logical-zone threads with `WRITE_ONCE` and read cross-thread with `READ_ONCE`.

Read or write failures generally enter VDO read-only mode through `set_persistent_error`, `enter_zone_read_only_mode`, or completion error handlers. A read-only rebuild is special: page-read failure is treated as an uninitialized page so rebuild can continue.

## Dependencies And Integration Points

The file depends on VDO's completion and work-queue system, `data_vio` request state, recovery journal, physical-zone allocator and PBN locks, VIO metadata I/O submitters, `int_map`, wait queues, admin-state/action-manager scheduling, block-map encodings, and slab-depot validation. It is called by the data path to locate and update mappings, by recovery/rebuild to traverse tree pages, by growth/configuration code to resize logical capacity, and by admin suspend/resume paths to drain metadata I/O.

## Risks And Edge Cases

- The page cache relies on strict logical-zone thread affinity; cross-thread callers can corrupt wait queues, LRU state, or counters.
- Busy counts, waiter queues, and deferred writes must stay balanced. A missing `vdo_release_page_completion` can pin a page and cause cache pressure or drain hangs.
- Error paths often move the VDO to read-only mode. Tests need to distinguish expected `VDO_NO_SPACE` from fatal corruption or I/O errors.
- `data_vio->recovery_sequence_number` is transferred into page recovery locks by `vdo_update_block_map_page`; losing that transfer can permit journal reap before map persistence.
- Dirty generation accounting uses 8-bit cyclic generation values; underflow/overflow checks enter read-only mode.
- `vdo_find_block_map_page_pbn` is only valid after allocated tree pages are loaded, as documented.
- `vdo_invalidate_page_cache` reallocates the map only after asserting there are no dirty pages; callers must drain/write first.
- Traversal repairs invalid entries by clearing them and writing the affected tree page, so recovery tests should expect mutation.

## Test Signals

Useful signals include block-map cache statistics (`pages_loaded`, `pages_saved`, `discard_required`, `wait_for_page`, `failed_reads`, `failed_writes`, `flush_count`), read-only transitions, persistent page-cache error logs, bad page or bad mapping logs, drain completion behavior, and recovery-journal reference balance. Coverage should exercise cached hits, incoming/outgoing waiters, dirty eviction with flush, read-only rebuild read errors, missing tree-page allocation, concurrent waiters for the same tree page, map growth/abandon, forest traversal repair, and data-path get/put mapping updates.
