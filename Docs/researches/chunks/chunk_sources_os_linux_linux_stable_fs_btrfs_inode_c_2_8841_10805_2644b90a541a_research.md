# Chunk Research: sources/os/linux/linux-stable/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of Linux-stable Btrfs `inode.c` in `Docs/research_subset_a.md` scope. It covers the VFS rename adapter, delayed allocation flushing across inode/root lists, symlink and tmpfile inode creation, preallocated file extent insertion, permission checks, encoded read/write helpers for compressed extents, swapfile activation/deactivation, inode byte and range-clean assertions, inode lookup by number, and final Btrfs operation tables for directory, file, special, symlink, address-space, and dentry behavior.

## APIs and Entry Points

- `btrfs_rename2()` is the VFS `.rename` entry point. It accepts `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`, dispatches to earlier `btrfs_rename_exchange()` or `btrfs_rename()`, then triggers dirty btree balancing.
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` expose delayed-allocation flushing to snapshot, qgroup, reclaim, ioctl, device-replace, and transaction paths.
- `btrfs_symlink()` creates symlink inodes backed by uncompressed inline extent data.
- `btrfs_prealloc_file_range()` and `btrfs_prealloc_file_range_trans()` wrap `__btrfs_prealloc_file_range()` to reserve disk extents and insert `BTRFS_FILE_EXTENT_PREALLOC` records with or without an existing transaction.
- `btrfs_permission()` enforces readonly-root and readonly-inode write denial before `generic_permission()`.
- `btrfs_tmpfile()` implements unnamed temporary file creation through orphan-backed new-inode setup and `d_tmpfile()`.
- Encoded I/O APIs include `btrfs_encoded_read()`, `btrfs_encoded_read_regular()`, `btrfs_encoded_read_regular_fill_pages()`, and `btrfs_do_encoded_write()`.
- Under `CONFIG_SWAP`, `.swap_activate` and `.swap_deactivate` are implemented by `btrfs_swap_activate()` and `btrfs_swap_deactivate()`; otherwise activation returns `-EOPNOTSUPP`.

## Control Flow

Delayed-allocation flushing serializes on root/filesystem delalloc mutexes, splices pending lists, grabs inode/root references, queues async flush work for unbounded flushes, or calls `filemap_flush_nr()` for bounded flushes. Reclaim callers may skip inodes flagged `BTRFS_INODE_NO_DELALLOC_FLUSH`.

Symlink creation allocates and initializes an inode, reserves new-inode metadata, starts a transaction, creates the inode, inserts a `BTRFS_EXTENT_DATA_KEY`, fills a `BTRFS_FILE_EXTENT_INLINE` item, instantiates the dentry, ends the transaction, and balances dirty btrees.

Preallocation reserves extents in chunks, inserts prealloc file extents, updates extent maps, decrements block-group reservations only after file extent insertion, and safely advances `i_size`/disk-i-size after marking the full old-to-new file-extent range.

Encoded read locks the inode and extent range, rejects or waits for ordered extents, resolves extent maps, handles inline data, holes/prealloc zeroing, compressed extents, and leaves locks held with `-EIOCBQUEUED` when the caller must submit disk I/O.

Encoded write validates compression/alignment/size constraints, copies compressed user data into compressed-write folios, waits and invalidates overlapping cache, reserves data/qgroup/metadata, tries inline COW, otherwise reserves disk space, creates an I/O extent map and encoded compressed ordered extent, updates `i_size`, and submits compressed write I/O.

Swap activation waits for ordered extents, rejects compressed/COW/checksummed files, blocks relocation/balance/device/snapshot races, rejects dead roots, locks the file range, verifies every extent is explicit, non-inline, uncompressed, unshared, single-profile, and on one device, then pins devices/block groups and registers physical swap extents.

## State and Dependencies

State touched includes delalloc inode/root lists, inode runtime flags, qgroup/data/metadata reservations, block-group reservation and swap counters, extent maps, file extent items, ordered extents, compressed bios, pagecache state, extent I/O locks, swapfile pin rb-trees, root swapfile counters, exclusive-operation state, snapshot locks, VFS inode bytes, and root inode xarrays.

In-file dependencies defined earlier include `btrfs_rename_exchange()`, `btrfs_rename()`, `insert_reserved_file_extent()`, `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, inline COW helpers, extent-map creation, and many callbacks used by the final operation tables.

Cross-file dependencies include `btrfs_replace_file_extents()` in `file.c`, `btrfs_alloc_ordered_extent()` in `ordered-data.c`, compressed-bio helpers in `compression.c/.h`, encoded ioctl/io_uring frontends in `ioctl.c`, share detection in `backref.c`, chunk mapping and swapfile-pin checks in `volumes.c`, and exclusive-operation helpers in `fs.c`.

## Risks and Cross-Chunk References

- Delalloc flushing depends on correct list restoration, reference handling, and async completion before freeing work items.
- Preallocation has fragile reservation and size-persistence ordering, especially around keep-size gaps and safe disk-i-size updates.
- Encoded read transfers lock ownership across `-EIOCBQUEUED`; callers must unlock exactly once.
- Encoded write tracks different logical, unencoded, and compressed disk byte counts, making unwind ordering error-prone.
- Swap activation must reject holes, inline extents, compression, shared/COW extents, multi-device/profile mappings, readonly/scrub-affected block groups, dead roots, and snapshot races to avoid direct swap I/O corruption.
- Earlier chunks of this same file define rename, new-inode, extent insertion, inline COW, read/write address-space callbacks, and other operation-table targets.
- `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()` are used by file extent replacement, reflink, tree-log, inode extent updates, and relocation code.