# Chunk Research: sources/local-fs/kdave-linux/fs/btrfs/inode.c lines 8841-10805

## Scope

This chunk is the tail of Btrfs inode/VFS implementation in `sources/local-fs/kdave-linux/fs/btrfs/inode.c`, within `Docs/research_subset_a.md` local filesystem scope. It covers rename dispatch, delayed allocation flushing, symlink and tmpfile creation, file preallocation extent insertion, permission checks, encoded read/write support, swapfile activation/deactivation, inode byte accounting/assertion helpers, inode lookup by number, and the final VFS operation tables for Btrfs directory/file/special/symlink inodes, address spaces, and dentries.

## APIs and Entry Points

- `btrfs_rename2()` is the VFS `.rename` adapter. It validates `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`, dispatches to `btrfs_rename_exchange()` or `btrfs_rename()`, then balances dirty btrees.
- `btrfs_start_delalloc_snapshot()` and `btrfs_start_delalloc_roots()` flush pending delayed allocation.
- `btrfs_symlink()` creates symlinks using inline extent data.
- `btrfs_prealloc_file_range()` and `_trans()` reserve disk extents and insert `BTRFS_FILE_EXTENT_PREALLOC`.
- `btrfs_permission()` enforces read-only root/inode state before `generic_permission()`.
- `btrfs_tmpfile()` creates unnamed orphan-backed temp files.
- Encoded I/O helpers implement compressed/inline/hole read paths and encoded compressed writes.
- `btrfs_swap_activate()` / `btrfs_swap_deactivate()` provide swapfile hooks when `CONFIG_SWAP` is enabled.
- Final operation tables bind directory, file, special, symlink, address-space, and dentry callbacks.

## Control Flow

Delayed allocation flushing serializes via root/fs delalloc mutexes, splices pending lists, grabs live inodes/roots, skips reclaim-protected inodes when needed, queues unlimited flush work or directly flushes bounded pagecache ranges, then restores unprocessed list entries.

Symlink and tmpfile creation use `btrfs_new_inode_args`, metadata reservation preparation, transactions, inode creation, and dirty btree balancing. Symlinks add an inline `BTRFS_EXTENT_DATA_KEY`; tmpfiles use orphan semantics and `d_tmpfile()`.

Preallocation reserves extents in chunks, releases qgroup data for the target range, inserts prealloc file extents through either an existing transaction or `btrfs_replace_file_extents()`, updates extent maps and inode metadata, and carefully updates file/disk size after marking the file extent range to avoid persisted size truncation from range gaps.

Encoded reads lock the inode and extent range, wait for or reject ordered extents, inspect extent maps, return inline data directly, zero-fill holes/prealloc extents, or leave locks held with `-EIOCBQUEUED` for later disk read submission. Encoded regular read I/O uses Btrfs bios over allocated pages with refcounted completion state.

Encoded writes validate compression/encryption/alignment/size constraints, copy compressed input into compressed-write folios, wait and invalidate overlapping cache, reserve data/qgroup/metadata, try inline COW if eligible, otherwise reserve disk space, create an I/O extent map and ordered compressed extent, update `i_size`, release reservations, and submit compressed write I/O.

Swap activation flushes ordered extents, requires `NODATACOW|NODATASUM` and no compression, blocks exclusive relocation/balance/device operations and snapshots, rejects dead roots, walks all file extents, verifies no holes/inline/compressed/shared/multi-device extents, pins the device and block groups, builds physical swap extents, and unwinds pins on error.

## State, Dependencies, Risks

State touched includes delalloc root/inode lists, inode runtime flags, qgroup/data/metadata reservations, block-group reservations, extent maps, ordered extents, compressed bios, inode size/version/ctime, swapfile rb-tree pins, block-group swap counters, root swapfile counts, and VFS inode byte counters.

Key dependencies include Btrfs transaction/new-inode helpers, qgroups, extent allocation and extent maps, ordered-data, compression, extent I/O locking, backref sharedness checks, chunk mapping, snapshot/exclusive-operation locks, directory/ioctl/xattr/ACL/fileattr helpers, and VFS pagecache APIs.

Main risks are reservation unwind ordering, lock ownership across `-EIOCBQUEUED`, deadlocks if btree paths are held during sharedness checks, swapfile corruption if mutable/shared/COW extents slip through, and persistence bugs around prealloc size extension without complete file-extent range tracking.

## Cross-Chunk References

- `btrfs_rename_exchange()` and `btrfs_rename()` are defined before this chunk.
- `btrfs_new_inode_prepare()`, `btrfs_create_new_inode()`, and `btrfs_new_inode_args_destroy()` are earlier in this file.
- `insert_reserved_file_extent()`, `btrfs_create_io_em()`, and many operation-table callbacks are earlier inode.c dependencies.
- `btrfs_replace_file_extents()` is in `fs/btrfs/file.c`.
- `btrfs_alloc_ordered_extent()` is in `fs/btrfs/ordered-data.c`.
- `btrfs_submit_compressed_write()` is in `fs/btrfs/compression.c`.
- Swapfile activation depends on snapshot, relocation, balance, device, scrub, chunk, backref, and block-group code outside this chunk.