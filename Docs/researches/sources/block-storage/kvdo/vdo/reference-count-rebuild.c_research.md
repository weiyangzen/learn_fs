# File Research: sources/block-storage/kvdo/vdo/reference-count-rebuild.c

Implements read-only reference-count rebuild from the VDO block map. It reconstructs slab refcounts by traversing block-map tree pages and leaf pages, repairing invalid mappings as needed, then flushing block-map changes.

Core object:
- `struct rebuild_completion` extends `vdo_completion` and stores block map/depot pointers, logical/admin thread IDs, counters returned to the caller, current page fetch state, outstanding reads, and an array of page completions.

Flow:
- `vdo_rebuild_reference_counts()` creates the rebuild completion, invalidates the block-map page cache to avoid deep completion chaining, then traverses the block-map forest.
- `process_entry()` handles interior block-map tree pages. Each tree-page PBN is validated as a physical data block and counted as `VDO_JOURNAL_BLOCK_MAP_INCREMENT` with refcount set to the block-map maximum reference value.
- After tree traversal, `rebuild_from_leaves()` computes the last legal block-map slot, launches a bounded number of asynchronous leaf-page fetches, and tracks outstanding requests.
- `rebuild_reference_counts_from_page()` processes every leaf page entry:
  - clears initialized mappings beyond the logical end,
  - clears invalid encoded locations,
  - skips unmapped and zero-block mappings,
  - clears mappings to non-data PBNs,
  - increments data refcounts for valid mapped PBNs,
  - counts logical blocks used.
- `finish_if_done()` waits for all fetches and outstanding work, then drains/flushes the block map through `vdo_drain_block_map()` on the admin thread.
- Errors mark the rebuild aborted, release page completions, and finish the parent with the saved result.

Notable design points:
- Leaf page completions keep pages locked until processed.
- Rebuild modifies block-map pages to remove bogus mappings and requests page writes for repairs.
- Refcount increments call `vdo_adjust_reference_count_for_rebuild()`, so normal-operation provisional/reference assumptions are relaxed.
