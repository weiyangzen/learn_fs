# Chunk Research: sources/local-fs/btrfs-linux/fs/btrfs/inode.c lines 1-8840

## Scope

This report covers `sources/local-fs/btrfs-linux/fs/btrfs/inode.c` lines 1-8840 for subset A (`Docs/research_subset_a.md`). The chunk spans Btrfs inode initialization, buffered writeback/delalloc, ordered extent completion, checksum validation, orphan and delayed-iput handling, VFS inode/directory operations, extent lookup, truncation, eviction, inode creation/link/unlink, subvolume deletion, getattr, and most rename logic. It stops immediately before `btrfs_rename2()` at line 8841.

## Public And Internal APIs Covered

- Locking wrappers: `btrfs_inode_lock()` / `btrfs_inode_unlock()` combine VFS inode locking with optional shared, trylock, and mmap write locking.
- Delalloc/writeback entry points: `btrfs_run_delalloc_range()`, `btrfs_set_extent_delalloc()`, `btrfs_split_delalloc_extent()`, `btrfs_merge_delalloc_extent()`, `btrfs_writepage_cow_fixup()`, `btrfs_finish_ordered_io()`, and `btrfs_finish_one_ordered()`.
- Extent APIs: `btrfs_get_extent()`, `can_nocow_extent()`, `btrfs_create_io_em()`, `btrfs_truncate_block()`, and `btrfs_cont_expand()`.
- Checksum APIs: `btrfs_calculate_block_csum_folio()`, `btrfs_calculate_block_csum_pages()`, `btrfs_check_block_csum()`, and `btrfs_data_csum_ok()`.
- Inode lifecycle APIs: `btrfs_iget()`, `btrfs_iget_path()`, `btrfs_alloc_inode()`, `btrfs_free_inode()`, `btrfs_destroy_inode()`, `btrfs_drop_inode()`, `btrfs_init_cachep()`, `btrfs_destroy_cachep()`, `btrfs_evict_inode()`.
- Namespace operations: `btrfs_lookup_dentry()`, `btrfs_lookup()`, `btrfs_unlink_inode()`, `btrfs_unlink()`, `btrfs_rmdir()`, `btrfs_create_new_inode()`, `btrfs_add_link()`, `btrfs_create()`, `btrfs_mknod()`, `btrfs_mkdir()`, `btrfs_link()`, `btrfs_delete_subvolume()`, `btrfs_rename_exchange()`, and `btrfs_rename()`.
- Attribute and metadata APIs: `btrfs_setattr()`, `btrfs_getattr()`, `btrfs_update_inode()`, `btrfs_update_inode_fallback()`, `btrfs_update_time()`, `btrfs_orphan_add()`, and orphan cleanup helpers.

## Control Flow And Behavior

- Read/checksum error reporting starts with generic data checksum diagnostics, with special data-relocation handling that resolves logical addresses through backrefs and prints affected roots, inodes, offsets, links, paths, or metadata tree refs.
- Buffered writeback begins at `btrfs_run_delalloc_range()`. It first attempts inline extent creation for small offset-zero ranges, then chooses NOCOW/prealloc if inode flags allow, async compression if compression policy/heuristics allow, and regular COW otherwise. Zoned filesystems use `run_delalloc_cow()` to allocate then immediately submit locked ranges.
- Inline COW (`run_delalloc_inline()` and `__cow_file_range_inline()`) drops existing extents, inserts an inline file extent, updates `disk_i_size`, inode bytes, qgroup reservation, and inode item state. `ret == 1` means inline was not possible and normal writeback should continue.
- Compressed writeback uses `async_cow` / `async_chunk` / `async_extent`: `compress_file_range()` compresses and records compressed or uncompressed fallback extents; ordered work later calls `submit_compressed_extents()` and `submit_one_async_extent()` to reserve disk space, create pinned IO extent maps, create ordered extents, submit bios, or fall back to uncompressed COW.
- Regular COW is split between `cow_file_range()` and `cow_one_range()`: reserve a data extent, lock the file range, create a pinned IO extent map, allocate an ordered extent, clone relocation checksums when needed, and clear/unlock delalloc state. Zoned `-EAGAIN` can mean no active zones; the first iteration waits, later iterations can return a partial done offset.
- NOCOW writeback (`run_delalloc_nocow()`) scans file extent items, checks snapshot generations, cross refs, checksums, encoding/compression, readonly block groups, and block-group NOCOW writer pins. Non-NOCOWable gaps are coalesced and flushed through `fallback_to_cow()`.
- Ordered extent completion (`btrfs_finish_one_ordered()`) is the main persistence point for writeback: it joins a transaction, handles zoned completion, inserts RAID stripe-tree extents, converts COW/prealloc/direct/encoded ordered state into file extent items or written prealloc extents, inserts pending checksums, updates inode size/bytes, handles truncation and IO errors, releases delalloc block-group bytes, frees reserved extents on failure, and removes ordered extent references.
- Directory lookup translates directory items to inode or root keys. Root keys cross subvolume boundaries via `fixup_tree_root_location()`; missing subvolume references can synthesize a dummy simple directory inode for placeholder entries.
- Directory readdir buffers entries into a page-sized private buffer to avoid `dir_emit()` faults while tree locks are held, merges delayed dir index insert/delete lists, and caps `ctx->pos` after the last visible entry to avoid returning newly-created entries during the same scan.
- Truncate and expansion have separate flows. Expansion zeroes partial old EOF blocks, inserts explicit hole extents unless `NO_HOLES`, updates extent maps, then updates `i_size` under `snapshot_lock`. Shrink waits ordered extents, updates page cache size, calls `btrfs_truncate()`, repeatedly truncates inode items with a temporary metadata reservation, handles partial final block zeroing outside the transaction, and marks full fsync when extents were dropped.
- Eviction first truncates page cache and extent state/maps, then deletes unlinked inode items in transactions with eviction-specific reservation rules. It leaves orphan items for next mount if cleanup cannot complete.
- Create/link/unlink operations are transaction-counted around inode item, inode ref/root ref, dir item/index, parent update, ACL/xattr/security, orphan item, and delayed inode work. `btrfs_create_new_inode()` reserves an xarray slot before publishing the inode into root inode cache.
- Subvolume deletion marks the destination root dead under `subvol_sem`, rejects default subvolume/send/swapfile cases, removes root refs and UUID-tree records, inserts a tree-root orphan item, frees anon bdev, invalidates dentries, and schedules dead-root cleanup.
- Rename exchange and normal rename pin log transactions for non-root entries to prevent replay windows where neither old nor new directory entry is logged. Root/subvolume renames force full log commit and are guarded by `subvol_sem`. Normal rename also supports whiteout by creating a char-device whiteout inode after the old entry is moved.

## State And Data Structures

- Per-inode state includes `extent_tree`, `io_tree`, optional `file_extent_tree`, `ordered_tree`, `block_rsv`, `delalloc_bytes`, `new_delalloc_bytes`, `defrag_bytes`, `csum_bytes`, `disk_i_size`, `dir_index`, `index_cnt`, `runtime_flags`, compression properties, root pointer, and delayed node/iput/list membership.
- Per-root and fs-wide state used here includes `root->inodes` xarray, `root->delalloc_inodes`, `root->nr_delalloc_inodes`, `fs_info->delalloc_roots`, `async_delalloc_pages`, `delayed_iputs`, `nr_delayed_iputs`, `subvol_sem`, `fs_roots_radix`, `reloc_mutex`, `data_sinfo`, block reservations, qgroup reservations, and cleaner/fixup/delalloc worker queues.
- Extent state flags drive accounting and correctness: `EXTENT_DELALLOC`, `EXTENT_DELALLOC_NEW`, `EXTENT_DEFRAG`, `EXTENT_NORESERVE`, `EXTENT_LOCKED`, `EXTENT_DO_ACCOUNTING`, `EXTENT_CLEAR_META_RESV`, `EXTENT_CLEAR_DATA_RESV`, `EXTENT_FINISHING_ORDERED`, `EXTENT_NODATASUM`, and `QGROUP_RESERVED`.
- Ordered extent flags distinguish `BTRFS_ORDERED_REGULAR`, `NOCOW`, `PREALLOC`, `COMPRESSED`, `DIRECT`, `ENCODED`, `TRUNCATED`, and `IOERR`. The code is careful about which cleanup path owns metadata/data/qgroup reservations for each flag mix.
- Btree item state touched in this chunk includes inode items, inode refs/extrefs, dir items, dir index items, file extent items, hole extents, orphan items, root refs/backrefs, root items, UUID-tree entries, csum items, and RAID stripe-tree extent records.

## Dependencies

- VFS/MM integration: inode/dentry/file operations, folios, address-space ops, page cache, `i_rwsem`, `i_mmap_lock`, `truncate_setsize()`, `pagecache_isize_extended()`, `filemap_flush()`, `generic_fillattr()`, `dir_emit()`, ACL, LSM xattrs, fscrypt, and migration hooks.
- Btrfs subsystems: transactions, delayed inode/items, ordered data, extent maps, extent I/O, compression, qgroups, relocation/backrefs, root tree, dir items, file items, inode items, tree log, UUID tree, orphan items, space/block groups, zoned allocator, RAID stripe tree, verity, subpage state, and free-space inode handling.
- Cross-file callers visible by search include `extent_io.c` for `btrfs_run_delalloc_range()` and `btrfs_get_extent()`, `bio.c` for `btrfs_data_csum_ok()`, `ordered-data.c` for `btrfs_finish_ordered_io()`, `direct-io.c` and `file.c` for `can_nocow_extent()` and extent lookup, `ioctl.c` for `btrfs_create_new_inode()`, and inode tests for `btrfs_get_extent()`.

## Risks And Invariants

- Reservation ownership is the largest risk surface: data space, metadata reservations, qgroup reservations, block-group `delalloc_bytes`, inode byte counts, and ordered-extent cleanup are intentionally split across writeback, ordered completion, truncate, invalidate, and eviction.
- Error paths must not clear `EXTENT_DO_ACCOUNTING`, metadata reservations, or data reservations from the wrong owner. Several paths deliberately avoid clearing flags because ordered extent completion owns the accounting.
- Lock ordering is fragile: extent locks precede transaction joins in ordered completion; path locks are released before memory allocation or long backref walks; delayed iput locks are IRQ-safe; inode/root/subvolume locks protect xarray, delalloc lists, and subvolume deletion.
- Log replay/fsync correctness depends on `last_unlink_trans`, `last_reflink_trans`, full-sync flags, log pinning during rename, `btrfs_record_unlink_dir()`, `btrfs_log_new_name()`, and forced full commits for subvolume/root renames.
- Inline extents are tightly constrained: offset 0 only, size at most filesystem sector and page, not full sector uncompressed, not encrypted, and must cover the whole file.
- NOCOW is conservative: it rejects shared/snapshotted/csum-bearing/compressed/encoded/readonly extents and prealloc ranges with overlapping delalloc. Misclassification risks stale checksums or writes into shared extents.
- Subpage/blocksize mismatches are explicitly handled in checksum, truncate, invalidate, and release paths. Waiting on the subpage spinlock before releasing folio private state avoids use-after-free with endio.
- Orphan cleanup has special cases for dead roots, fsverity metadata, historical truncate orphan items, and reused inode numbers. Failure leaves orphan items for later mount cleanup.
- Rename and exchange have replay windows if log pinning or full-commit forcing is wrong. Whiteout creation also has a delayed cleanup path through `btrfs_new_inode_args_destroy()` and `iput()`.

## Cross-Chunk References

- The chunk ends just before `btrfs_rename2()` at line 8841. Later code wires `btrfs_rename()` / `btrfs_rename_exchange()` into VFS inode operations and balances dirty btrees after rename.
- Later same-file sections outside this chunk define delalloc root flushing, symlink creation, preallocation/fallocate helpers, permission/tmpfile handlers, encoded read/write, swapfile activation, inode byte helpers, `btrfs_find_first_inode()`, and final operation tables. This chunk calls or prepares state for several of those later APIs.
- `btrfs_update_inode_bytes()` and `btrfs_assert_inode_range_clean()` are referenced here but defined later in the file, so final per-file research should connect inode byte accounting and extent-state assertions back to the writeback/truncate paths above.
- `btrfs_file_operations` is assigned in this chunk but defined in another file; `btrfs_aops` and inode operation tables are declared here but defined after the chunk boundary.