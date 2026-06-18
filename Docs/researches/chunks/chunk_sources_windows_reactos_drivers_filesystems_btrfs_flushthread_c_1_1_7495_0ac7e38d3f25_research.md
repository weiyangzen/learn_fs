# Chunk Research: sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c lines 1-7495

## Scope

This report covers `sources/windows/reactos/drivers/filesystems/btrfs/flushthread.c` lines 1-7495 for subset A (`Docs/research_subset_a.md`). The chunk spans most of the WinBtrfs/ReactOS Btrfs flush path: physical writes, TRIM batching, dirty btree COW extent allocation and refcount conversion, tree splitting/merging, tree and superblock serialization, changed extent/checksum/chunk usage flushing, FCB and file-reference metadata batching, chunk creation/deletion, RAID5/6 partial-stripe completion, subvolume/root-ref updates, disk-cache flushing, device stats, orphan cleanup, and the prologue of `do_write2()`. It stops at line 7495 inside debug timing setup for `do_write2()`.

## APIs And Control Flow

- Physical IO helpers build and submit IRPs directly: `write_data_phys()`, `write_completion()`, `ioctl_completion()`, `flush_disk_caches()`, and superblock write helpers.
- Free-space cleanup merges chunk `deleting` ranges back into free-space lists and optionally maps them into per-device TRIM ranges. RAID0/10 and duplicate-like profiles are handled; RAID5/6 TRIM mapping is left as a FIXME.
- Tree flushing is COW-based: `add_parents()`, `allocate_tree_extents()`, `update_tree_extents()`, `do_splits()`, `write_trees()`, and `write_superblocks()` mark dirty ancestors, allocate fresh metadata blocks, convert refs, rebalance trees, serialize nodes, write metadata, and then persist superblocks.
- Metadata extent allocation prefers the original writable non-reloc chunk, scans matching existing chunks, then allocates a new metadata/system chunk if needed.
- Shared-tree conversion updates tree/data refs and changed-extent tracking so later extent-tree flushing can reconcile old and new refs.
- `do_tree_writes()` coalesces adjacent tree buffers, calls `write_data()`, waits for stripe IO, logs device write errors, and flushes RAID56 partial stripes.
- `add_checksum_entry()` rewrites overlapping `EXTENT_CSUM` ranges by deleting old items, overlaying new checksums or holes in a bitmap, and reinserting capped runs.
- `flush_fcb()` handles ADS xattrs, deleted inodes, extent checksums, extent merge/rationalization, sparse holes, inode item updates, security/DOS/reparse/EA/compression/case-sensitive xattrs, arbitrary xattrs, and orphan marking.
- `flush_fileref()` translates file-reference create/delete/rename/type changes into batched `DIR_ITEM`, `DIR_INDEX`, `INODE_REF`, `ROOT_REF`, and `ROOT_BACKREF` updates.
- `create_chunk()` and `drop_chunk()` add/remove chunk-tree, extent-tree, dev-tree, bootstrap, device accounting, free-space cache, TRIM, and incompat-flag state.
- RAID56 helpers read or reconstruct missing stripe data, zero unallocated/deleting ranges, write data stripes, and compute/write parity.
- `test_not_full()` implements a metadata reserve check to avoid COW dead-end full-filesystem states.
- `check_for_orphans_root()` opens orphan items, excises extents for zero-link files, marks FCBs deleted/dirty, deletes orphan items, and rolls back extent changes on error.

## State And Dependencies

Key state includes `Vcb->superblock`, roots, chunks, devices, dirty FCBs/filerefs, system chunk bootstrap entries, dirty trees, changed extents, partial stripes, rollback lists, batch lists, and per-FCB inode/extent/xattr fields.

The chunk depends on Windows kernel IRP, MDL, event, resource, pool, ATA pass-through, DSM TRIM, and bitmap APIs. It also depends on Btrfs driver helpers for tree search/update, extent refcounts, rollback, free-space lists, chunk allocation/cache loading, physical RAID writes, FCB lifecycle, and checksum/parity functions.

## Risks And Invariants

- Metadata COW correctness depends on precise refcount/ref-type conversion, especially for shared backrefs and unique-tree detection.
- Space accounting spans chunks, block groups, roots, superblock bytes used, device bytes used, free-space caches, and rollback lists.
- Batch item ownership is delicate: buffers become owned by the batch on success and must be freed only on failed insertion.
- `flush_fcb()` rewrites extent metadata broadly; hole insertion and extent merging rely on exact sector alignment and no-holes semantics.
- RAID56 partial-stripe reconstruction can corrupt parity if bitmap runs, degraded reads, or zero-fill ranges are wrong.
- TRIM is best-effort and clears local lists even though per-device discard failures are not propagated in detail.
- Several delete/reinsert flows must avoid using invalidated `traverse_ptr` item memory after deletion.
- `drop_chunk()` frees chunks during list iteration, so saved next pointers and lock-release ordering are critical.

## Cross-Chunk References

- Lines after 7495 complete `do_write2()`, final flush transaction ordering, rollback, batch commit, superblock writes, cache flushing, readonly transition, `do_write()`, `do_flush()`, and `flush_thread()`.
- `commit_batch_list()` and `clear_batch_list()` are used here but defined elsewhere; they should be linked to `insert_tree_item_batch()` in the merged report.
- `write_data()` and stripe structures are used by `do_tree_writes()` but defined outside this range.
- `update_changed_extent_ref()` and `add_changed_extent_ref()` are central to extent accounting here but are defined outside this chunk.