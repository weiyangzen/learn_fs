# sources/distributed-fs/ceph-client/drivers/md/dm-vdo/block-map.h

## Purpose

`block-map.h` declares the VDO block-map data structures and public API. It documents the design: a set of radix trees, distributed across logical zones, with a per-zone leaf-page cache and single-threaded zone ownership for normal lookup/update operations.

## Important APIs, Types, And Functions

- Constants and exports: `BLOCK_MAP_VIO_POOL_SIZE`, `vdo_page_generation`, and `UNMAPPED_BLOCK_MAP_ENTRY`.
- `struct vdo_page_cache`: per-zone cache for leaf block-map pages, including page arrays, PBN map, LRU/free/outgoing lists, I/O counters, waiters, and `block_map_statistics`.
- `enum vdo_page_buffer_state` and `enum vdo_page_write_status`: cache page lifecycle and write intent.
- `struct page_info`: one cache slot, including metadata VIO, PBN, busy count, waiters, list entries, and recovery-journal lock.
- `struct vdo_page_completion`: caller-owned request for a cache page, with readiness and writable state.
- `struct tree_page`, `struct dirty_lists`, `struct block_map_zone`, and `struct block_map`: interior tree page storage, dirty-era tracking, per-zone block-map state, and the top-level map.
- Public operations: page get/release/write/invalidate, slot lookup, map page PBN lookup, tree page write, forest traversal, decode/record/free, journal initialization, era advance, drain/resume, growth, mapping get/put, page update, and statistics.
- `vdo_convert_maximum_age`: converts old recovery-journal age tuning to the current journal entry density.

## Control Flow

The header splits responsibilities between cache-page operations (`vdo_get_page` through `vdo_invalidate_page_cache`), tree/forest operations (`vdo_find_block_map_slot`, `vdo_write_tree_page`, `vdo_traverse_forest`), lifecycle operations (`vdo_decode_block_map`, `vdo_free_block_map`, drain/resume/grow), and mapping operations (`vdo_get_mapped_block`, `vdo_put_mapped_block`, `vdo_update_block_map_page`). Callers are expected to run load/save operations on the admin thread and normal mapping operations on the owning logical-zone thread.

## State And Persistence Behavior

The declared state mirrors persistent block-map pages and journal coupling. `page_info::recovery_lock` and `tree_page::recovery_lock` hold the earliest journal sequence needed by an unwritten page. `dirty_lists` bins cache and tree pages by recovery-journal era and expires old pages for writeback. `block_map` records the root origin/count for persisted map roots, the nonce used to validate pages, current/pending era points, active and prepared forests, and per-zone state.

## Dependencies And Integration Points

The header imports admin state, completions, encodings, int maps, statistics, VIOs, wait queues, and VDO numeric/types definitions. It is included by data-path code, recovery/growth code, and metadata-management code that needs to translate logical blocks, update mappings, or traverse allocated block-map pages.

## Risks And Edge Cases

- The single-threaded zone model is part of the API contract, not just an implementation detail.
- `struct block_map` uses a flexible array of zones; allocation must match the logical-zone count.
- `struct vdo_page_completion` is both a completion and a wait-queue entry, so callers must not reuse it while queued or ready.
- Dirty-era arrays are sized by `maximum_age`; invalid zero or very small values would break expiration assumptions.
- `vdo_convert_maximum_age` multiplies `age` before division; callers should use sane configured values.

## Test Signals

Compile-time signals include type visibility, enum size assumptions, and prototypes matching `block-map.c`. Behavioral tests should validate completion ownership, page-release requirements, dirty-era aging, conversion of maximum age, growth preparation/replacement, and statistics aggregation across zones.
