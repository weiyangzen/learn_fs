# Chunk Research: sources/os/linux/linux/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/os/linux/linux/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans Btrfs inode support from includes and local helper state through checksum diagnostics, buffered writeback/delalloc, COW/NOCOW/compression decisions, ordered extent completion, delayed iput and orphan cleanup, inode load/update, namespace operations, truncation/expansion, eviction, lookup/readdir, new inode creation, extent lookup, folio invalidation, inode cache lifecycle, getattr, and most rename logic. The chunk stops immediately before `btrfs_rename2()` at line 8841.

## Public And Internal APIs Covered

- Lock wrappers: `btrfs_inode_lock()` and `btrfs_inode_unlock()` combine VFS inode `i_rwsem` locking with Btrfs flags for shared, trylock, and mmap write locking.
- Writeback and delalloc entry points: `btrfs_run_delalloc_range()`, `btrfs_set_extent_delalloc()`, `btrfs_writepage_cow_fixup()`, `btrfs_finish_ordered_io()`, and `btrfs_finish_one_ordered()`.
- Extent mapping APIs: `btrfs_get_extent_allocation_hint()`, `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, `btrfs_truncate_block()`, and `btrfs_cont_expand()`.
- Checksum APIs: `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()`.
- Inode lifecycle APIs: `btrfs_iget()`, `btrfs_iget_path()`, `btrfs_alloc_inode()`, `btrfs_destroy_inode()`, `btrfs_drop_inode()`, and `btrfs_evict_inode()`.
- Namespace operations: lookup, unlink, rmdir, create, mknod, mkdir, hardlink, subvolume deletion, rename exchange, and normal rename.

## Control Flow And Behavior

- `btrfs_run_delalloc_range()` dispatches buffered writeback. It tries inline extent creation, then NOCOW/prealloc writeback, then async compression, and finally regular COW. Zoned filesystems use a path that allocates and immediately writes locked ranges.
- Inline writeback validates strict constraints: offset zero, small enough for sector/page/max-inline limits, whole-file coverage, and not encrypted. It may compress one sector, drop overlapping extents, insert an inline file extent, update inode bytes and `disk_i_size`, and return `1` to fall back to normal extent writeback.
- Async compression uses `async_cow`, `async_chunk`, and `async_extent`. Compression work clears dirty state, compresses chunks, rejects compression unless it saves space, and later submits compressed bios or falls back to uncompressed COW.
- Regular COW reserves data extents, locks file ranges, creates pinned IO extent maps, allocates ordered extents, clones relocation checksums when needed, and clears delalloc state.
- NOCOW scans file extent items and rejects unsafe targets: inline, shared, snapshotted, csum-bearing, compressed, encrypted, encoded, explicit-hole, or readonly extents. Unsafe gaps are coalesced and sent through COW fallback.
- Ordered extent completion persists writeback results: handles IO errors, zoned completion, truncation, transactions, RAID stripe-tree records, NOCOW inode updates, prealloc conversion, COW file extent insertion, checksum insertion, inode byte updates, reservation cleanup, and ordered extent reference removal.
- Orphan cleanup walks orphan items, handles dead roots, fsverity metadata, historical truncate orphan items, and inode reuse, relying on eviction-triggered `iput()` for real unlink cleanup.
- Inode loading fills VFS/Btrfs inode state from btree or delayed inode state, marks pessimistic fsync state after reload, initializes extent tracking, selects operation tables, and inserts the inode into the root xarray.
- Namespace operations update dir items, dir indexes, inode/root refs, link counts, parent sizes, timestamps, inode versions, tree-log delete records, and orphan items.
- Truncation/expansion zero partial EOF blocks, insert holes unless `NO_HOLES`, update extent maps, wait ordered extents, drop file extent items, and mark full fsync when extents were removed.
- Folio release/invalidation waits writeback and subpage spinlock users, accounts ordered extents that will never be submitted, frees qgroup reservations, and avoids clearing extent state still needed by ordered completion.

## State And Data Structures

- Per-inode state includes `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, `disk_i_size`, `dir_index`, `index_cnt`, runtime flags, compression properties, delayed node/iput membership, and root pointer.
- Per-root/fs state includes `root->inodes`, delalloc inode/root lists, async delalloc counters, delayed iputs, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, block reservations, qgroup reservations, and worker queues.
- Key extent flags include `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_FINISHING_ORDERED`, and `EXTENT_NODATASUM`.
- Ordered extent flags distinguish regular COW, NOCOW, prealloc, compressed, direct, encoded, truncated, and IO-error states.
- Btree item types manipulated include inode items, inode refs/extrefs, dir items, dir index items, file extent items, hole extents, orphan items, root refs/backrefs, root items, UUID-tree entries, checksum items, and RAID stripe-tree extent records.

## Dependencies

- VFS/MM: inode/dentry/file ops, folios, address-space ops, page cache, `i_rwsem`, `i_mmap_lock`, truncate helpers, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACLs, fscrypt, LSM xattrs, fsverity cleanup, migration hooks, and whiteout support.
- Btrfs subsystems: transactions, delayed inode/items, ordered data, extent maps, extent I/O, compression, qgroups, relocation/backrefs, root tree, dir/file/inode items, tree log, UUID tree, orphan items, block groups, zoned allocator, RAID stripe tree, verity, subpage state, and property inheritance.
- External users continue outside this chunk: writeback and extent lookup from extent I/O, checksum validation from bio handling, ordered completion from ordered-data code, and NOCOW/IO extent setup from file/direct/encoded write paths.

## Risks And Invariants

- Reservation ownership is the highest-risk area: data space, metadata, qgroup reservations, block-group delalloc bytes, inode bytes, and ordered extent refs are split across multiple phases.
- Error paths must clear only the flags they own; several paths intentionally leave accounting for ordered extent completion or reserved-extent cleanup.
- Lock ordering is fragile: extent locks precede transaction joins in ordered completion; btree paths are released before long operations; delayed iput locking is IRQ-safe; `subvol_sem` serializes subvolume deletion/rename with snapshot operations.
- Fsync/log replay correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning during rename/exchange, and forced full commits for root entries.
- NOCOW must stay conservative or it can write into shared data or leave stale checksums.
- Subpage/blocksize mismatches are explicitly handled in checksum, truncate, invalidate, release, and folio dirty/ordered logic.

## Cross-Chunk References

- This chunk ends immediately before `btrfs_rename2()` at line 8841.
- Later same-file code wires rename helpers into VFS operations and continues with delalloc root flushing, symlink creation, preallocation/fallocate, permission/tmpfile handling, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and operation tables.
- `btrfs_update_inode_bytes()` and `btrfs_assert_inode_range_clean()` are referenced here but defined later.
- `btrfs_find_first_inode()` is called by subvolume deletion pruning here and defined later.
- `btrfs_file_operations` is assigned here but defined elsewhere; `btrfs_aops` and inode operation tables are declared in this chunk and defined after the boundary.