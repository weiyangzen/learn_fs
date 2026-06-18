# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.c

## Purpose
Low-level implementation shared by disk and metadata space maps. It stores per-block reference counts using bitmap blocks for small counts and an overflow btree for larger counts.

## On-Disk Format
- Bitmap index:
  - Each `disk_index_entry` points to a bitmap block and stores `nr_free` plus `none_free_before`.
  - Metadata space maps store a fixed array of index entries in one metadata index block.
  - Disk space maps store index entries in a btree and cache them in memory.
- Bitmap block:
  - `disk_bitmap_header` with checksum and block number.
  - Two bits per metadata block:
    - `0`: unused
    - `1`: refcount 1
    - `2`: refcount 2
    - `3`: overflow / many
- Overflow refcount btree:
  - Maps block number to a 32-bit little-endian refcount for counts above 2.

## Validators
- `index_validator` checks metadata index block checksum and block location.
- `dm_sm_bitmap_validator` checks bitmap block checksum and block location.

## Major Functions
- `sm_ll_init()`: initializes common `ll_disk` fields and btree descriptors.
- `sm_ll_extend()`: adds bitmap blocks and index entries for newly addressable blocks.
- `sm_ll_lookup_bitmap()` and `sm_ll_lookup()`: read bitmap and overflow counts.
- `sm_ll_find_free_block()` scans index entries and bitmap blocks for a free block.
- `sm_ll_find_common_free_block()` ensures allocation is free in both old and current transaction views.
- `sm_ll_insert()`: sets an exact refcount, maintaining bitmap, overflow btree, free counts, and allocation delta.
- `sm_ll_inc()` / `sm_ll_dec()`: range refcount mutation with per-bitmap chunking and overflow handling.
- `sm_ll_commit()`: writes changed index state.
- `sm_ll_new_metadata()` / `sm_ll_open_metadata()`: fixed-index metadata-space-map setup.
- `sm_ll_new_disk()` / `sm_ll_open_disk()`: btree-index disk-space-map setup.

## Important Behavior
- `none_free_before` accelerates free scanning inside bitmap blocks.
- `nr_allocated` is updated when refcount transitions between zero and nonzero.
- Overflow manipulation uses `btree_get_overwrite_leaf()` when possible for in-place update of an already-shadowed leaf.
- Bitmap locks may be temporarily dropped while acquiring overflow btree leaves because overflow updates can allocate metadata.
- Disk index-entry cache has 64 direct-mapped entries and writes dirty entries back on eviction/commit.

## Role in Repository
This file is the allocator/refcount engine used by both metadata-block space maps and data-block space maps.
