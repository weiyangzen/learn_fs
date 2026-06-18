# File Research: sources/block-storage/kvdo/vdo/block-map-tree.c

## Purpose

Implements the interior tree machinery used to find, load, allocate, dirty, flush, and recover block map pages.

## Main Responsibilities

- Initializes and tears down per-zone block map tree state.
- Maintains dirty lists by recovery-journal era.
- Maintains a metadata VIO pool for interior tree I/O.
- Tracks pages currently being loaded/allocated using an integer-key lock map.
- Loads interior pages from disk and validates them.
- Allocates missing block map tree pages for writes.
- Journals block map page allocations through recovery and slab journals.
- Writes dirty tree pages with generation/flush ordering.
- Handles read-only transition on metadata I/O or invariant failures.
- Provides direct lookup of leaf block map page PBNs after tree pages are loaded.

## Key Concepts

- `struct page_descriptor` is packed into a 64-bit lock key identifying root, height, page index, and slot.
- `loading_pages` maps page keys to the active `tree_lock` so concurrent lookups can wait behind the first loader/allocator.
- Dirty pages have cyclic 8-bit generations. The zone tracks dirty counts per generation to know which pages are covered by flushes.
- `zone->flusher` identifies the page issuing or about to issue a flush.
- `VDO_INVALID_PBN` marks a loaded root-location pseudo page.

## Important Functions

- `vdo_initialize_tree_zone()` creates dirty lists, loading map, and VIO pool.
- `vdo_uninitialize_block_map_tree_zone()` frees tree-zone resources.
- `vdo_copy_valid_page()` validates and copies a disk page into an in-memory tree page.
- `vdo_is_tree_zone_active()` reports active lookups, waiters, or VIO use.
- `vdo_advance_zone_tree_period()` advances dirty-list era periods.
- `vdo_drain_zone_trees()` flushes dirty lists unless suspending.
- `vdo_lookup_block_map_pbn()` walks/loads/allocates the block-map tree to locate a leaf block map page.
- `vdo_find_block_map_page_pbn()` finds a leaf page PBN from already loaded tree pages.
- `vdo_write_tree_page()` schedules an interior page write during read-only rebuild corrections.

## Lookup and Allocation Flow

`vdo_lookup_block_map_pbn()` computes the root and tree slots for a logical page. If an in-memory tree page is present and initialized, it validates the next mapping. If the child page is mapped, it either finishes or loads the next level. If unmapped and the VIO is a write, it allocates missing pages; reads/trims simply finish as unmapped.

Allocation flow:
1. Acquire page lock in `loading_pages`.
2. Allocate a physical data block in the appropriate allocated zone.
3. Add a recovery journal entry.
4. Add a slab journal entry and set max reference count protection.
5. Release allocation lock.
6. Update parent tree page entry.
7. Format newly allocated child page in memory if needed.
8. Wake waiters sharing the page lock.

## Writeback Flow

Dirty-list expiration calls `write_dirty_pages_callback()`, which assigns the current generation and enqueues pages. `write_page()` copies the in-memory page into a VIO buffer, captures generation and recovery lock, clears the in-memory recovery lock, and submits metadata I/O.

On completion, recovery journal block references are released. If the page was dirtied again while writing, it is requeued. If a flush page completes, waiting pages may be written if not dirtied since the flush generation.

## Error Behavior

Metadata I/O errors call `record_metadata_io_error()` and transition the zone to read-only mode. Read-only mode drains flush waiters so the tree zone can close.

## Dependencies and Interactions

- Integrates with `block-map.c` for page updates and drain completion checks.
- Uses `forest` for in-memory tree pages.
- Uses `dirty-lists`, `int-map`, VIO pools, recovery journal, slab journal, and data VIO allocation callbacks.
- Relies on block map page validation/formatting helpers.

## Notable Edge Cases

- Reads waiting behind an allocation failure that is `VDO_NO_SPACE` may complete successfully because the mapping remains unmapped.
- Non-space allocation/load failures force read-only behavior for writers.
- Root pages are not checked as physical data blocks.
- Newly allocated block map pages are protected from deduplication by setting max references before writeout.
- Generation arithmetic is cyclic and guarded by assertions.
