<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h

## Purpose
Declares the shared low-level space-map disk format and helper interface used by both disk and metadata space-map wrappers.

## Important APIs, Types, And Functions
`struct disk_index_entry` maps a bitmap index to a bitmap block and stores `nr_free` plus `none_free_before`. `struct disk_metadata_index` is the compact fixed metadata-index block containing up to `MAX_METADATA_BITMAPS` entries. `struct disk_sm_root` is the root persisted by wrappers and stores total blocks, allocated blocks, bitmap root, and overflow refcount root. `struct disk_bitmap_header` is the header for bitmap blocks.

`struct ll_disk` contains the transaction manager, bitmap and refcount btree infos, block geometry, current roots, backend function pointers, index cache, and changed flags. Backend callbacks abstract whether bitmap index entries live in a fixed metadata-index block or a btree/cache.

Declared low-level APIs initialize/open metadata or disk variants, extend space, lookup counts, find free blocks, insert counts, increment/decrement ranges, and commit cached/index state.

## Control Flow
Wrappers initialize `ll_disk` through either metadata or disk constructors, then call shared operations for all count and allocation changes. Backend function pointers route index-entry load/save/commit operations to the correct persistence shape.

## State And Persistence
The header describes the persistent encoding: two bits per block in bitmap blocks, overflow counts in a separate btree, and roots summarized in `disk_sm_root`. It also defines runtime caching state for disk index entries.

## Dependencies And Integration Points
The header depends on `dm-btree.h` and is consumed by `dm-space-map-common.c`, `dm-space-map-disk.c`, and `dm-space-map-metadata.c`.

## Risks
Changing these structures changes on-disk metadata compatibility. Alignment, packing, and little-endian fields are part of the disk format. `MAX_METADATA_BITMAPS` bounds metadata-space size, and wrappers must enforce it.

## Test Signals
Tests should validate serialized root sizes, endian conversions, metadata max-block limits, disk and metadata backend equivalence for count operations, and index cache behavior around dirty entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.h -->
