<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c -->
# sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c

## Purpose
Implements the low-level on-disk space-map engine shared by disk and metadata space maps. It tracks per-block reference counts using compact bitmap blocks for counts 0, 1, 2, and overflow, plus a btree for counts greater than 2.

## Important APIs, Types, And Functions
Validators `index_validator` and `dm_sm_bitmap_validator` protect metadata-index and bitmap blocks with checksum and expected block-number checks. Bitmap helpers `sm_lookup_bitmap()`, `sm_set_bitmap()`, `sm_find_free()`, and `dm_bitmap_word_used()` manage two-bit entries inside bitmap blocks.

The main shared state is `struct ll_disk`, declared in the header. Exported low-level functions include `sm_ll_extend()`, `sm_ll_lookup_bitmap()`, `sm_ll_lookup()`, `sm_ll_find_free_block()`, `sm_ll_find_common_free_block()`, `sm_ll_insert()`, `sm_ll_inc()`, `sm_ll_dec()`, `sm_ll_commit()`, `sm_ll_new_metadata()`, `sm_ll_open_metadata()`, `sm_ll_new_disk()`, and `sm_ll_open_disk()`.

Range updates use `struct inc_context` to hold a shadowed bitmap block and optional overflow-tree leaf. Overflow helpers update the refcount btree in place through `btree_get_overwrite_leaf()` when possible. The disk-index variant uses a 64-entry cache of btree index entries; the metadata-index variant keeps a fixed `disk_metadata_index` block in memory.

## Control Flow
Initialization sets up two btree infos: one for bitmap index entries and one for overflow refcounts. `sm_ll_extend()` increases logical blocks, allocates new bitmap blocks through the transaction manager, initializes index entries, and saves them through the configured index backend.

Lookups locate the bitmap index entry, read the bitmap block, and return the two-bit count. Count value `3` means the true count is in the overflow btree. Inserts shadow the relevant bitmap, update the two-bit entry, insert/remove overflow entries as needed, adjust `nr_allocated`, `nr_free`, and `none_free_before`, and save the index entry. Range inc/dec loops operate bitmap by bitmap, shadowing once per bitmap and reopening write locks when overflow tree operations temporarily release the bitmap.

`sm_ll_commit()` flushes dirty index-entry state through the backend. Metadata mode commits the fixed metadata index by shadowing its index block. Disk mode writes back dirty cached index entries into the bitmap-index btree.

## State And Persistence
Persistent state consists of `disk_sm_root`, bitmap index entries, bitmap blocks, and overflow refcount btree roots. `nr_blocks` and `nr_allocated` describe total and allocated blocks. `none_free_before` accelerates free searches within a bitmap. All metadata updates are copy-on-write through the transaction manager.

## Dependencies And Integration Points
This file depends on btree internals, transaction-manager shadowing/refcounts, block-manager validators, device-mapper logging, and Linux bitops. It is wrapped by `dm-space-map-disk.c` for general data blocks and `dm-space-map-metadata.c` for metadata self-allocation.

## Risks
Reference-count transitions around 2/3 are delicate because they move counts between the bitmap and overflow btree. Any missed overflow insert/remove corrupts sharing semantics. `nr_allocated`, `nr_free`, and `none_free_before` must stay synchronized with bitmap mutations or allocation can leak blocks or report false free space. Disk index cache writeback must not lose dirty entries. Allocating a block that was free only in the current transaction is prevented by higher wrappers comparing old and current maps.

## Test Signals
Tests should exercise count transitions 0->1->2->3->4 and back to 0, range inc/dec across bitmap boundaries, overflow btree leaf reuse, free-block searches with `none_free_before`, metadata and disk index commit paths, index cache collisions/writeback, checksum/blocknr corruption, and extension near backend max-entry limits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/md/persistent-data/dm-space-map-common.c -->
