# Chunk Research: sources/local-fs/btrfs-linux/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of Btrfs inode/VFS implementation in `sources/local-fs/btrfs-linux/fs/btrfs/inode.c`, within `Docs/research_subset_a.md` local filesystem scope. It covers rename dispatch, delayed allocation flushing, symlink and tmpfile creation, file preallocation extent insertion, permission checks, encoded read/write support, swapfile activation/deactivation, inode byte accounting/assertion helpers, inode lookup by number, and the final VFS operation tables for Btrfs directory/file/special/symlink inodes, address spaces, and dentries.

## APIs and Entry Points

- `btrfs_rename2()` is the VFS `.rename` adapter. It validates `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`, dispatches to `btrfs_rename_exchange()` or `btrfs_rename()`, then balances dirty btrees.
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` flush pending delayed allocation for one root during snapshotting or across all roots for writeback/reclaim.
- `btrfs_symlink()` implements VFS symlink creation using an inline `BTRFS_EXTENT_DATA_KEY` item containing the target path.
- `btrfs_prealloc_file_range()` and `btrfs_prealloc_file_range_trans()` reserve disk extents and insert `BTRFS_FILE_EXTENT_PREALLOC` records, with or without a caller-supplied transaction.
- `btrfs_permission()` enforces read-only root and inode flags before delegating to `generic_permission()`.
- `btrfs_tmpfile()` implements unnamed temporary file creation through Btrfs new-inode/orphan machinery and `d_tmpfile()`.
- `btrfs_encoded_io_compression_from_extent()`, `btrfs_encoded_read()`, `btrfs_encoded_read_regular()`, `btrfs_encoded_read_regular_fill_pages()`, and `btrfs_do_encoded_write()` implement encoded I/O paths for compressed extents and holes.
- `btrfs_swap_activate()` and `btrfs_swap_deactivate()` are installed as address-space swap hooks when `CONFIG_SWAP` is enabled; otherwise activation returns `-EOPNOTSUPP`.
- `btrfs_update_inode_bytes()` atomically adjusts VFS inode block usage counters after extent replacement operations.
- `btrfs_assert_inode_range_clean()` is an assertion helper for callers that have fully flushed and locked a file range.
- `btrfs_find_first_inode()` returns a referenced in-memory inode at or after a requested inode number.
- The chunk ends by defining `btrfs_dir_inode_operations`, `btrfs_dir_file_operations`, `btrfs_aops`, `btrfs_file_inode_operations`, `btrfs_special_inode_operations`, `btrfs_symlink_inode_operations`, and `btrfs_dentry_operations`.

## Control Flow

`btrfs_rename2()` is a thin flag gate. Unsupported flags immediately return `-EINVAL`; exchange renames call the dedicated exchange path, while normal/no-replace/whiteout renames call the main rename helper. Dirty metadata balancing is performed against the destination directory root before returning.

Delayed allocation flushing is coordinated by `start_delalloc_inodes()`. It serializes with `root->delalloc_mutex`, splices `root->delalloc_inodes` into a private list, then cycles each inode back to the root list before attempting an `igrab()`. Reclaim-context callers skip inodes with `BTRFS_INODE_NO_DELALLOC_FLUSH`. Snapshot flushes set `BTRFS_INODE_SNAPSHOT_FLUSH`. Unlimited flushes allocate `btrfs_delalloc_work`, queue work on `fs_info->flush_workers`, and later wait for every completion; bounded flushes call `filemap_flush_nr()` directly and stop on error or when the write budget reaches zero. Any unprocessed spliced entries are appended back under the delalloc spinlock.

`btrfs_start_delalloc_roots()` applies that inode-level logic across `fs_info->delalloc_roots`. It splices the global root list, grabs each root, moves it back to the global list, drops the root-list spinlock while flushing inodes, then puts the root. It preserves unprocessed roots on early exit. Both public delalloc entry points refuse work on a filesystem already in error state with `-EROFS`.

`btrfs_symlink()` creates a new inode, initializes it as a symlink, sets Btrfs address-space operations, records the symlink size, prepares new-inode metadata reservations, starts a transaction, creates the inode item, then inserts one inline file extent item at offset zero. The inline extent is marked uncompressed/unencrypted, its `ram_bytes` is the symlink length, and the target bytes are copied directly into the leaf. On path allocation or insert failure after inode creation, it aborts the transaction and discards the new inode.

Preallocation is split between `insert_prealloc_file_extent()` and `__btrfs_prealloc_file_range()`. The insert helper builds an in-memory `btrfs_file_extent_item` with `BTRFS_FILE_EXTENT_PREALLOC`, releases qgroup data for the file range, then either inserts into an existing transaction through `insert_reserved_file_extent()` or calls `btrfs_replace_file_extents()` to create/extend a transaction. Early failures free the qgroup reservation that was released at function entry. The range-level helper reserves disk extents in chunks capped at 256 MiB and adjusted by `min_size` and previous allocation size, inserts each prealloc extent, decrements block-group reservations only after extent insertion, installs an extent map when possible, updates allocation hints, ctime, inode version, and `BTRFS_INODE_PREALLOC`, and optionally extends `i_size`. Before extending size, it explicitly marks the file extent range covering old-to-new size so `btrfs_inode_safe_disk_i_size_write()` cannot persist a smaller size because of a gap left by prior keep-size preallocation.

## State and Synchronization

- Delalloc state is held in `root->delalloc_inodes` and `fs_info->delalloc_roots`, protected by paired mutexes and spinlocks. Workqueue flushes retain inodes with `igrab()` and release them in `btrfs_run_delalloc_work()`.
- Snapshot-related delalloc flushing uses `BTRFS_INODE_SNAPSHOT_FLUSH`; reclaim avoidance uses `BTRFS_INODE_NO_DELALLOC_FLUSH`; asynchronous compressed/delayed extents may force a second `filemap_flush()`.
- Symlink and tmpfile creation rely on `btrfs_new_inode_args` lifecycle, transaction item counts, VFS new-inode state, and Btrfs inline extent item state.
- Preallocation updates qgroup reservations, data-space reservations, block-group reservations, extent maps, inode size/disk size, ctime, inode version, and `BTRFS_INODE_PREALLOC`.
- Encoded I/O coordinates inode locks, extent locks, ordered extents, page cache invalidation/writeback, compressed bios, qgroup/delalloc accounting, and `ki_pos` advancement.
- Swapfile activation uses `i_mmap_lock`, extent I/O tree locks, `btrfs_exclop_start()/finish()`, `root->snapshot_lock`, `root->root_item_lock`, atomic `root->nr_swapfiles`, `fs_info->swapfile_pins_lock`, rb-tree pin storage, block-group swap extent counters, device references, and backref share checks.

## Dependencies

This chunk depends on VFS APIs, Linux concurrency primitives, and Btrfs subsystems from earlier code and other files.

Important Btrfs-local dependencies include transaction helpers, new-inode helpers, delayed allocation lists, qgroup accounting, extent allocation/freeing, block-group reservation and swap counters, extent maps, ordered extents, compressed write/read bio helpers, inline COW helpers, extent I/O tree locking, root snapshot/exclusive-operation locking, chunk mapping, backref sharedness checks, scrub state, inode item updates, file-extent tree tracking, dirty btree balancing, io_uring encoded-read completion, ACL/xattr/fileattr helpers, directory iteration/open/release/sync helpers, and dentry deletion policy.

## Risks and Edge Cases

- `start_delalloc_inodes()` has intentionally slow whole-list behavior and can skip reclaim-sensitive inodes, so callers must tolerate partial flushing in reclaim contexts.
- Symlink targets must fit both Btrfs inline limits and the filesystem sector size. No NUL byte is stored as part of the inline extent; the length is exactly `strlen(symname)`.
- Preallocation relies on careful reservation ordering: block-group reservations are decremented after file extent insertion to avoid relocation races, and qgroup release must be freed manually on early errors.
- Encoded read leaves inode and extent locks held when it returns `-EIOCBQUEUED` for non-hole disk reads. Correct callers must finish through the regular read path and unlock there.
- Encoded writes reject uncompressed/no-compression encoded data, encrypted data, NODATASUM files, badly aligned offsets, overly large extents, and compressed data that is not smaller than unencoded data.
- Swapfile activation rejects holes, inline extents, compressed extents, shared data extents, multi-device/profile mappings, extents crossing devices, and read-only/scrub-pinned block groups.
- `btrfs_swap_activate()` must release the btree path before `btrfs_is_data_extent_shared()` to avoid deadlocks with transaction joins and delayed item flushing.
- The address-space operations deliberately omit `.bmap`; exposing mutable Btrfs logical mappings to generic swapfile bmap users would risk corruption.

## Cross-Chunk References

- `btrfs_rename2()` depends on `btrfs_rename_exchange()` and `btrfs_rename()` defined before this chunk.
- Delalloc list membership, inode runtime flags, root/fs-info delalloc list management, and delayed iput behavior are established earlier in this file and surrounding Btrfs writeback code.
- `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, and `btrfs_new_inode_args_destroy()` are defined earlier and govern symlink/tmpfile transaction reservations and orphan behavior.
- Preallocation calls `insert_reserved_file_extent()`, `btrfs_replace_file_extents()`, extent-map replacement, qgroup helpers, and inode file-extent range tracking implemented outside this chunk.
- Encoded read/write entry points are likely called from ioctl or file-operation code outside this line range; this chunk implements the inode-side mechanics but not the userspace ioctl dispatcher.
- Swapfile activation ties into snapshot creation, relocation, balance, device replace/remove/resize, scrub, and block-group code outside this file through exclusive operations, snapshot locks, swapfile pin checks, and block-group swap counters.
- The operation tables at the end reference many functions defined in earlier chunks of `inode.c` and connect this chunk's local implementations into the kernel VFS.