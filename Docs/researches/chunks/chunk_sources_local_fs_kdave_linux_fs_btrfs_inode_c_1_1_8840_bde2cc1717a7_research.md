# Chunk Research: sources/local-fs/kdave-linux/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/local-fs/kdave-linux/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans Btrfs inode initialization, buffered writeback/delalloc, ordered extent completion, checksum validation, orphan and delayed-iput handling, VFS inode/directory operations, extent lookup, truncation, eviction, inode creation/link/unlink, subvolume deletion, getattr, and most rename logic. It stops immediately before `btrfs_rename2()` at line 8841.

The corresponding `sources/local-fs/btrfs-linux/fs/btrfs/inode.c` file is byte-identical in this checkout; the kdave-linux line range was still treated as the authoritative chunk for this report.

## Public And Internal APIs Covered

- Locking wrappers: `btrfs_inode_lock()` / `btrfs_inode_unlock()` combine VFS inode locking with optional shared, trylock, and mmap write locking.
- Delalloc/writeback entry points: `btrfs_run_delalloc_range()`, `btrfs_set_extent_delalloc()`, `btrfs_split_delalloc_extent()`, `btrfs_merge_delalloc_extent()`, `btrfs_writepage_cow_fixup()`, `btrfs_finish_ordered_io()`, and `btrfs_finish_one_ordered()`.
- Extent APIs: `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, `btrfs_truncate_block()`, and `btrfs_cont_expand()`.
- Checksum APIs: `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()`.
- Inode lifecycle APIs: `btrfs_iget()`, `btrfs_iget_path()`, `btrfs_alloc_inode()`, `btrfs_free_inode()`, `btrfs_destroy_inode()`, `btrfs_drop_inode()`, `btrfs_init_cachep()`, `btrfs_destroy_cachep()`, `btrfs_evict_inode()`.
- Namespace operations: `btrfs_lookup_dentry()`, `btrfs_lookup()`, `btrfs_unlink_inode()`, `btrfs_unlink()`, `btrfs_rmdir()`, `btrfs_create_new_inode()`, `btrfs_add_link()`, `btrfs_create()`, `btrfs_mknod()`, `btrfs_mkdir()`, `btrfs_link()`, `btrfs_delete_subvolume()`, `btrfs_rename_exchange()`, and `btrfs_rename()`.

## Control Flow And Behavior

- Buffered writeback begins at `btrfs_run_delalloc_range()`: inline extent attempt, NOCOW/prealloc path, async compression path, or regular COW path.
- Inline COW drops existing extents, inserts inline file extent metadata, updates `disk_i_size`, inode bytes, qgroup reservation, and inode item state.
- Compressed writeback uses `async_cow`, `async_chunk`, and `async_extent`; ordered work reserves disk space, creates pinned IO extent maps and ordered extents, submits bios, or falls back to uncompressed COW.
- Regular COW reserves data extents, locks file ranges, creates IO extent maps, adds ordered extents, clones relocation checksums when needed, and clears delalloc state.
- NOCOW scans file extent items and rejects unsafe cases including shared/snapshotted/csum-bearing/compressed/encoded/readonly extents.
- Ordered extent completion is the main persistence point: joins a transaction, handles zoned completion, inserts file extents/checksums, updates inode size/bytes, handles truncation and IO errors, releases reservations, and drops ordered references.
- Directory lookup maps directory items to inode or root keys, including subvolume-root fixups and dummy simple directory inodes for missing placeholder subvolume refs.
- Readdir buffers entries outside tree locks, merges delayed dir index mutations, and caps `ctx->pos` after visible entries.
- Truncate/expand paths zero partial blocks, insert holes when needed, update extent maps and `i_size`, wait ordered extents, drop file extents, and mark full fsync when extents were removed.
- Eviction truncates page cache and extent state/maps, then deletes unlinked inode items with eviction-specific reservation handling.
- Create/link/unlink/subvolume delete/rename paths coordinate transactions, inode refs, dir items, delayed inode work, orphan items, root refs, UUID-tree records, log pinning, and subvolume locks.

## State And Data Structures

- Per-inode state includes `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, `disk_i_size`, `dir_index`, `index_cnt`, `runtime_flags`, compression settings, root pointer, and delayed-iput/list state.
- Per-root/fs state includes `root->inodes`, `root->delalloc_inodes`, `fs_info->delalloc_roots`, delayed iput queues, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, data space info, block reservations, qgroup reservations, and worker queues.
- Extent flags include `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, reservation-clear flags, `EXTENT_FINISHING_ORDERED`, `EXTENT_NODATASUM`, and `QGROUP_RESERVED`.
- Ordered extent flags distinguish regular, NOCOW, prealloc, compressed, direct, encoded, truncated, and IO-error cases.
- Btree state touched includes inode items, refs/extrefs, dir items/indexes, file extents, hole extents, orphan items, root refs/backrefs, root items, UUID-tree entries, csum items, and RAID stripe-tree records.

## Dependencies

- VFS/MM: inode/dentry/file operations, folios, address-space operations, page cache, `i_rwsem`, `i_mmap_lock`, truncate/pagecache helpers, `dir_emit()`, ACL, LSM xattrs, fscrypt, and migration hooks.
- Btrfs subsystems: transactions, delayed inode/items, ordered data, extent maps, extent I/O, compression, qgroups, relocation/backrefs, root tree, directory/file/inode items, tree log, UUID tree, orphan items, space/block groups, zoned allocator, RAID stripe tree, verity, subpage state, and free-space inode handling.
- Cross-file callers include `extent_io.c`, `bio.c`, `ordered-data.c`, `direct-io.c`, `file.c`, `ioctl.c`, and inode tests.

## Risks And Invariants

- Reservation ownership is the largest risk surface: data space, metadata reservations, qgroup reservations, block-group `delalloc_bytes`, inode byte counts, and ordered cleanup are split across writeback, ordered completion, truncate, invalidate, and eviction.
- Error paths must not clear accounting or reservation flags owned by ordered extent completion.
- Lock ordering is fragile around extent locks, transactions, path locks, delayed iput locks, inode/root locks, and `subvol_sem`.
- Fsync/log replay correctness depends on unlink/reflink transaction markers, full-sync flags, rename log pinning, `btrfs_record_unlink_dir()`, `btrfs_log_new_name()`, and full commits for subvolume/root renames.
- Inline extents are tightly constrained: offset zero, small enough for sector/page limits, not encrypted, and covering the whole file.
- NOCOW misclassification risks stale checksums or writes into shared extents, so checks are intentionally conservative.
- Subpage/blocksize handling appears in checksum, truncate, invalidate, and folio release paths.
- Orphan cleanup handles dead roots, fsverity metadata, historical truncate orphan items, and reused inode numbers; failures can leave orphan items for mount-time cleanup.
- Rename/exchange replay windows are mitigated through log pinning/full commits; whiteout creation has its own cleanup path.

## Cross-Chunk References

- This chunk ends just before `btrfs_rename2()` at line 8841.
- Later same-file code defines delalloc root flushing, symlink creation, preallocation/fallocate helpers, permission/tmpfile handlers, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and final operation tables.
- `btrfs_update_inode_bytes()` and `btrfs_assert_inode_range_clean()` are referenced here but defined later.
- `btrfs_file_operations` is assigned here but defined outside this chunk; `btrfs_aops` and inode operation tables are declared here and defined after the boundary.