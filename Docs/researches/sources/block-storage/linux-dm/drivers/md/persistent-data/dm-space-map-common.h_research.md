# File Research: sources/block-storage/linux-dm/drivers/md/persistent-data/dm-space-map-common.h

## Purpose
Shared low-level declarations and on-disk structures for space-map implementations.

## Main Definitions
- `struct disk_index_entry`: bitmap block pointer plus free-space summary.
- `struct disk_metadata_index`: checksummed fixed array of metadata index entries.
- `struct ll_disk`: shared low-level space-map state, including transaction manager, bitmap and overflow btree info, block geometry, roots, cached metadata index, callbacks, and index-entry cache.
- `struct disk_sm_root`: compact persistent root containing block count, allocated count, bitmap root, and refcount root.
- `struct disk_bitmap_header`: checksummed bitmap block header.
- Function pointer types for loading/saving/opening/committing index variants.

## Constants
- `MAX_METADATA_BITMAPS = 255`
- `IE_CACHE_SIZE = 64`
- `ENTRIES_PER_BYTE = 4`

## Exposed Internal Functions
Low-level extend, lookup, find-free, insert, inc/dec, commit, and create/open functions for metadata and disk variants.

## Role in Repository
This header separates shared low-level space-map mechanics from the two public wrappers: `dm-space-map-disk.c` and `dm-space-map-metadata.c`.
