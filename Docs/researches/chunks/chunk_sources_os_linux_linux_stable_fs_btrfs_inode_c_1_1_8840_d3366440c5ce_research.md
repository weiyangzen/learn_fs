# Chunk Research: sources/os/linux/linux-stable/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/os/linux/linux-stable/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans the start of Btrfs inode support through checksum diagnostics, inode locking, buffered writeback and delayed allocation, COW/NOCOW/compressed extent setup, ordered extent completion, delayed iput and orphan cleanup, inode load/update, unlink/rmdir/subvolume deletion, truncation and expansion, eviction, lookup/readdir, inode creation/link/mkdir/mknod, extent lookup, NOCOW checks, folio invalidation/release, inode cache lifecycle, getattr, rename exchange, and most of normal rename. The chunk stops immediately before `btrfs_rename2()` at line 8841.

## Public And Internal APIs Covered

- Locking/state helpers: `btrfs_inode_lock()`, `btrfs_inode_unlock()`, delalloc extent set/clear/split/merge helpers.
- Writeback/delalloc APIs: `btrfs_run_delalloc_range()`, `btrfs_writepage_cow_fixup()`, ordered extent finish helpers, inline/compressed/COW/NOCOW paths.
- Extent/checksum APIs: `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, truncate/expand helpers, block checksum calculation/validation.
- Inode lifecycle APIs: `btrfs_iget*()`, alloc/free/destroy/drop inode, cache init/destroy, eviction.
- Namespace/VFS ops: lookup, opendir/readdir, dirty/update-time, create, mknod, mkdir, link, unlink, rmdir, subvolume deletion, rename exchange, and normal rename.

## Control Flow And Behavior

- `btrfs_run_delalloc_range()` dispatches buffered writeback: inline extent attempt, NOCOW/prealloc, async compression, then regular COW. Zoned filesystems use allocation plus immediate locked-range submission.
- Inline writeback is limited to offset-zero, one-folio/page, sector-sized-or-smaller, whole-file, unencrypted data, and falls back on metadata ENOSPC.
- Compression records `async_extent` work, rejects poor compression ratios unless forced/property-driven, then submits compressed ordered extents or falls back to uncompressed COW.
- NOCOW is conservative: it rejects shared/snapshotted, csum-bearing, compressed/encrypted/encoded, explicit-hole, readonly, or unsafe prealloc ranges, then COWs unsafe gaps.
- Ordered extent completion persists writeback into the btree: handles IO errors, truncation, zoned completion, RAID stripe-tree records, file extent insertion/prealloc conversion, checksum insertion, inode byte/size updates, and reservation cleanup.
- Orphan cleanup scans orphan items, skips dead roots, cleans incomplete fsverity metadata, deletes obsolete truncate-orphan entries, and relies on eviction via `iput()` for unlinked inodes.
- Inode loading fills VFS/Btrfs state, sets pessimistic fsync replay markers after reload, initializes extent tracking, assigns operation tables, and publishes into `root->inodes`.
- Truncate/expand zero partial blocks, insert holes unless `NO_HOLES`, manipulate extent maps, wait ordered extents, and force full fsync when extents are dropped.
- Rename/exchange count transaction items, handle root refs vs inode refs, pin tree logs for non-root renames, force full commits for subvolume/root entries, and support whiteout creation.

## State And Data Structures

- Per-inode: `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, delalloc/new/defrag/csum byte counters, `disk_i_size`, `dir_index`, `index_cnt`, runtime flags, compression policy, delayed iput/node state, root pointer, and log transaction fields.
- Per-root/fs: inode xarray, delalloc inode/root lists, async delalloc counters, delayed iputs, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, block reservations, qgroup reservations, and worker queues.
- Extent flags: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, reservation-clear flags, `EXTENT_FINISHING_ORDERED`, and `EXTENT_NODATASUM`.
- Ordered extent flags distinguish regular, NOCOW, prealloc, compressed, direct, encoded, truncated, and IO-error states.

## Dependencies

- VFS/MM: inode/dentry/file ops, folios, page cache, locks, truncate helpers, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACLs, fscrypt, LSM xattrs, fsverity, migration, and whiteout support.
- Btrfs subsystems: transactions, delayed items, ordered data, extent maps/I/O trees, compression, qgroups, relocation/backrefs, root/dir/file/inode items, tree log, UUID tree, orphan items, block groups, zoned allocator, RAID stripe tree, verity, subpage state, and properties.
- Cross-file users include extent I/O writeback, bio checksum validation, ordered-data completion, direct/file/encoded write paths, and ioctl/subvolume creation paths.

## Risks And Invariants

- Reservation ownership is the main risk: metadata, data-space, qgroup, delalloc block-group bytes, inode bytes, and ordered extent refs are split across phases.
- Error paths must clear only owned flags; some paths intentionally leave accounting for ordered completion.
- Lock ordering is fragile around extent locks, transaction joins, btree paths, delayed iput IRQ locking, `subvol_sem`, folio writeback, and subpage spinlocks.
- Fsync/log replay correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning, unlink records, and forced full commits for root entries.
- Stable-specific note: this linux-stable chunk uses `icount_read(&inode->vfs_inode)` in `btrfs_prune_dentries()`, while the sibling mainline chunk uses `icount_read_once()`.

## Cross-Chunk References

- This chunk ends before `btrfs_rename2()` at line 8841.
- Later same-file code defines delalloc root flushing, symlink creation, preallocation/fallocate, permission/tmpfile handlers, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and operation tables.
- `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()` are referenced here but defined later.
- `btrfs_file_operations` is assigned here but defined elsewhere; `btrfs_aops` and inode operation tables are declared here and defined after the chunk boundary.