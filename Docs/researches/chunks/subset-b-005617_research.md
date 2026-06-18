# sources/distributed-fs/ceph-client/fs/btrfs/inode.c lines 8841-10803

## Scope

This chunk covers the tail of Btrfs inode operation implementation. It starts at the VFS `rename2` dispatcher and runs through delalloc flushing helpers, symlink and tmpfile creation, file preallocation, permission checks, encoded read/write support, swapfile activation/deactivation, inode byte accounting helpers, inode lookup by minimum object id, and the final VFS operation tables for directories, files, special inodes, symlinks, address spaces, and dentries.

The range is functionally dense and provides several exported integration points used outside this file: `btrfs_start_delalloc_snapshot()`, `btrfs_start_delalloc_roots()`, `btrfs_prealloc_file_range()`, `btrfs_prealloc_file_range_trans()`, encoded I/O helpers declared in `btrfs_inode.h`, `btrfs_update_inode_bytes()`, `btrfs_assert_inode_range_clean()`, and `btrfs_find_first_inode()`.

## Purpose

This section connects Btrfs inode state to Linux VFS operations and low-level extent machinery. It turns high-level file-system requests into Btrfs transactions, extent items, ordered extents, qgroup reservations, extent-map updates, and delayed writeback. It also exposes specialized entry points for send/receive and ioctl encoded I/O, and enforces the restrictions required to let a Btrfs file be used safely as swap.

The chunk is also where final operation tables bind previously defined functions from the full file to VFS callbacks. The merge lane should treat this as the end-of-file integration point: many callbacks named here are implemented in earlier chunks, while helpers implemented here are called from `file.c`, `ioctl.c`, `send.c`, and other Btrfs modules.

## Important APIs, Types, and Functions

`btrfs_rename2()` is the VFS rename callback wrapper. It accepts only `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, and `RENAME_WHITEOUT`; dispatches exchange renames to `btrfs_rename_exchange()` and all other accepted cases to `btrfs_rename()`; then calls `btrfs_btree_balance_dirty()` on the destination root's filesystem.

`struct btrfs_delalloc_work`, `btrfs_run_delalloc_work()`, `btrfs_alloc_delalloc_work()`, `start_delalloc_inodes()`, `btrfs_start_delalloc_snapshot()`, and `btrfs_start_delalloc_roots()` implement root-wide or filesystem-wide flushing of inodes that have delayed allocation. The code walks `root->delalloc_inodes` and `fs_info->delalloc_roots`, grabs inode/root references, optionally queues async work on `fs_info->flush_workers`, and honors `BTRFS_INODE_NO_DELALLOC_FLUSH` when called from reclaim context.

`btrfs_symlink()` creates symlinks as uncompressed inline extent data. It validates that the target length fits Btrfs inline limits and the filesystem sector size, initializes the VFS inode, prepares and creates the Btrfs inode item, inserts a `BTRFS_EXTENT_DATA_KEY` item at offset zero, writes the symlink bytes into the inline extent, and instantiates the dentry.

`insert_prealloc_file_extent()`, `__btrfs_prealloc_file_range()`, `btrfs_prealloc_file_range()`, and `btrfs_prealloc_file_range_trans()` implement fallocate-style preallocation. They reserve extents, insert `BTRFS_FILE_EXTENT_PREALLOC` file extent items, release qgroup data reservations into the transaction, update extent maps with `EXTENT_FLAG_PREALLOC`, advance `i_size` when `FALLOC_FL_KEEP_SIZE` is not set, maintain `disk_i_size` safety with `btrfs_inode_set_file_extent_range()`, update ctime and inode version, and commit per-extent transactions when the caller did not provide one.

`btrfs_permission()` denies writes to regular files, directories, and symlinks when the root is readonly or the inode has `BTRFS_INODE_READONLY`, then defers ordinary checks to `generic_permission()`.

`btrfs_tmpfile()` creates unnamed temporary regular files. It uses `btrfs_new_inode_args` with `.orphan = true`, creates the inode in a transaction, temporarily sets nlink to one to satisfy `d_tmpfile()` expectations, attaches the file dentry, unlocks the new inode, marks it dirty, balances dirty B-tree state, and returns through `finish_open_simple()`.

`btrfs_encoded_io_compression_from_extent()` maps on-disk Btrfs compression identifiers to the encoded I/O ABI. It supports none, zlib, zstd, and LZO variants keyed by sector size; unsupported or corrupt compression values fail with `-EINVAL` or `-EUCLEAN`.

`btrfs_encoded_read_inline()`, `struct btrfs_encoded_read_private`, `btrfs_encoded_read_endio()`, `btrfs_encoded_read_regular_fill_pages()`, `btrfs_encoded_read_regular()`, and `btrfs_encoded_read()` implement the read side of the encoded I/O ioctl and io_uring paths. They return either inline extent data, zeroes for holes/prealloc extents, raw compressed extent bytes with compression metadata, or raw uncompressed bytes from disk-backed extents. The regular read helper can submit one or more bios and uses a refcounted private completion object for synchronous and io_uring completion.

`btrfs_do_encoded_write()` writes pre-compressed data supplied through the encoded write path. It validates the encoded ABI, compression type, encryption absence, inode checksum compatibility, sizes, sector alignment, and encoded offsets; copies compressed input into compressed-bio folios; waits for and invalidates conflicting page cache and ordered extents; reserves data, qgroup, and metadata; optionally writes an inline compressed extent; otherwise reserves a physical extent, creates an extent map and encoded compressed ordered extent, updates `i_size`, unlocks the range, and submits the compressed write.

Under `CONFIG_SWAP`, `btrfs_add_swapfile_pin()`, `btrfs_free_swapfile_pins()`, `struct btrfs_swap_info`, `btrfs_add_swap_extent()`, `btrfs_swap_activate()`, and `btrfs_swap_deactivate()` implement Btrfs swapfile support. They validate that the file is nocow, nodatasum, uncompressed, hole-free, non-inline, unshared, single-device, and backed by a single data profile; pin the backing device and block groups in `fs_info->swapfile_pins`; prevent snapshots and exclusive operations that could move extents; and register contiguous physical ranges with the kernel swap subsystem. Without `CONFIG_SWAP`, activation returns `-EOPNOTSUPP`.

`btrfs_update_inode_bytes()` atomically updates VFS inode byte counters under `btrfs_inode::lock`, for clone/dedupe/zero-range style extent replacement paths.

`btrfs_assert_inode_range_clean()` is an assertion helper that checks, when Btrfs assertions are enabled, that no ordered extent overlaps a range that callers believe is fully flushed, waited, and locked.

`btrfs_find_first_inode()` walks `root->inodes` with the XArray API and returns an `igrab()`'d Btrfs inode whose object id is at least a caller-supplied minimum.

The operation tables at the end bind Btrfs implementations into VFS dispatch: `btrfs_dir_inode_operations`, `btrfs_dir_file_operations`, `btrfs_aops`, `btrfs_file_inode_operations`, `btrfs_special_inode_operations`, `btrfs_symlink_inode_operations`, and `btrfs_dentry_operations`.

## Control Flow

Delalloc flushing uses two nested list-walk patterns. `btrfs_start_delalloc_roots()` splices the global `fs_info->delalloc_roots` list while holding `delalloc_root_mutex` and `delalloc_root_lock`, grabs each root, moves it back to the tail for fairness, drops the spinlock while flushing that root, and restores unfinished spliced roots on exit. `start_delalloc_inodes()` does the same at per-root inode granularity. Full snapshot flushing passes `nr_to_write == NULL`, queues a `btrfs_delalloc_work` for each grabbed inode, then waits for all queued completions before returning. Bounded flushing calls `filemap_flush_nr()` directly and stops when the write budget is exhausted or an error appears.

Symlink and tmpfile creation follow the standard Btrfs new-inode transaction pattern: allocate and initialize a VFS inode, run `btrfs_new_inode_prepare()` to reserve ids and delayed metadata, start a transaction sized by the preparation step, create the inode item, add extra records when needed, instantiate or attach the dentry, end the transaction, destroy the new-inode argument state, and drop the inode on error.

Preallocation loops until the requested range is covered. Each iteration caps the allocation request at 256 MiB, honors the minimum extent size, adapts to the previous allocation size under fragmentation, reserves a data extent, inserts a prealloc extent item, decrements block-group reservations only after the file extent item exists, updates the in-memory extent map if possible, updates inode metadata, and either ends its own transaction or reuses the caller transaction. Error paths free only the still-uncovered reserved data range and release qgroup reservations that were moved out of data reservation but never attached to a transaction.

Encoded read first locks the inode in shared mode, normalizes the starting offset to sector alignment, locks enough extent state to cover the maximum compressed extent size, and waits or returns `-EAGAIN` for ordered extents depending on `IOCB_NOWAIT`. It then resolves the extent map. Inline extents are read from the leaf and copied after dropping path and locks. Holes and prealloc extents return zeroes. Disk-backed extents leave locks held and return `-EIOCBQUEUED` so the ioctl/uring layer can call `btrfs_encoded_read_regular()` or complete the async flow with the resolved disk address and size.

Encoded write validates before modifying filesystem state, then serializes against existing ordered extents and page cache by waiting, invalidating, locking the range, and rechecking. After resource reservation it tries an inline compressed extent when the encoded range exactly matches the unencoded range and inline COW is allowed. Otherwise it reserves disk space, creates a compressed extent map, allocates an ordered extent marked `BTRFS_ORDERED_ENCODED` and `BTRFS_ORDERED_COMPRESSED`, updates `i_size` if the logical write extends EOF, releases delalloc accounting, and submits the compressed bio. The cleanup ladder unwinds in reverse order: reserved extent, delalloc extents and metadata, qgroup data, data-space reservation, extent lock, and compressed bio.

Swap activation serializes aggressively. It takes `i_mmap_lock` after the VFS inode lock, waits all ordered extents, validates immutable inode flags, starts an exclusive operation, takes the root snapshot write lock, increments `root->nr_swapfiles` only after checking that the root is not being deleted, locks the whole sector-aligned file range, then walks file extent items from offset zero to EOF. Each extent is checked for hole/inline/compression/share violations, mapped to a physical stripe, constrained to single profile and one device, pinned through the global swapfile pin tree, coalesced into contiguous physical swap extents, and periodically rescheduled. On any failure after `nr_swapfiles` is incremented, `btrfs_swap_deactivate()` frees pins and decrements the counter before locks are dropped.

## State and Persistence Behavior

The functions in this chunk persist Btrfs metadata through transactions and B-tree item updates. Symlinks persist their target as an inline `BTRFS_FILE_EXTENT_INLINE` extent. Preallocation persists `BTRFS_FILE_EXTENT_PREALLOC` items with disk bytenr, disk length, logical length, ram bytes, generation, and no compression; it also updates inode flags, ctime, i_version, `i_size`, and disk size when appropriate. Encoded writes persist compressed file extent metadata through ordered extent completion and update in-memory extent maps before I/O submission.

Delayed allocation state is maintained in per-root and per-fs lists guarded by mutexes and spinlocks. Work items hold temporary inode references until flushing completes, and direct flushing uses delayed iput to avoid dropping references in unsafe contexts. Snapshot flushes set `BTRFS_INODE_SNAPSHOT_FLUSH` on inodes being flushed.

Qgroup accounting is explicit in preallocation and encoded write. Prealloc insertion calls `btrfs_qgroup_release_data()` and transfers released data reservation into extent replacement or reserved extent insertion; early failures free the released refroot reservation. Encoded write reserves qgroup data for the logical range and frees it on failure before the write becomes ordered.

Swapfile state is partly persistent and partly runtime-only. The file extents already exist on disk, but activation builds runtime pins in `fs_info->swapfile_pins`, increments per-root `nr_swapfiles`, increments per-block-group swap extent counts, and assigns `sis->bdev`, `sis->max`, `sis->pages`, and span values for the swap subsystem. These pins are intentionally transient and are removed by swap deactivation.

Inode byte accounting is protected by `inode->lock` so concurrent `stat(2)` sees consistent `i_blocks`-style values while extent replacement adds and removes bytes. The final operation tables are static dispatch state compiled into the filesystem module.

## Dependencies and Integration Points

This chunk depends heavily on Btrfs core subsystems: transaction handles, path and extent-buffer manipulation, extent maps, ordered extents, delayed allocation accounting, qgroups, block-group reservations, compressed bio submission, chunk mapping, snapshot locks, exclusive-operation state, root/inode XArrays, and B-tree balancing. It also depends on VFS/MM primitives such as inodes, dentries, kiocbs, iov iters, folios/pages, bios, address-space operations, swap activation callbacks, inode locks, mmap locks, and generic permission helpers.

External users inside Btrfs include:

- `file.c`, which routes encoded write requests to `btrfs_do_encoded_write()`.
- `ioctl.c`, which drives encoded read/write ioctls and io_uring encoded reads using `btrfs_encoded_read()` and `btrfs_encoded_read_regular()`.
- `send.c`, which uses encoded read helpers to copy compressed extents without decompressing them.
- fallocate and extent-replacement paths that call the preallocation helpers and `btrfs_update_inode_bytes()`.
- snapshot, reclaim, transaction commit, and sync paths that call the delalloc flushing entry points.
- VFS dispatch through the inode/file/address-space/dentry operation tables.

The final callback tables connect this chunk to many earlier functions in the same file: lookup/create/unlink/link/mkdir/rmdir/mknod/getattr/setattr/listxattr/ACL/update-time/fileattr/readdir/open/release/fsync/read/writepage/readahead/invalidate/launder/release/migrate callbacks are all assembled here even when their implementations live outside this range.

## Risks

- Delalloc list walking is lock-sensitive. Incorrect splice restoration, root/inode reference handling, or spinlock dropping can lose inodes from flush lists, deadlock flush paths, or use freed roots/inodes.
- Full snapshot flushing queues async work and waits for all completions. Missing waits or failed work allocation paths can leave snapshot-sensitive delalloc unflushed.
- Preallocation has subtle qgroup and block-group reservation sequencing. Decrementing block-group reservations before inserting the file extent can race relocation; failing to free released qgroup reservation on early error leaks quota reservation.
- The `disk_i_size` update in preallocation relies on marking the file extent range before increasing size. Regressions here can persist a smaller disk size than VFS `i_size` after remounts when old keep-size prealloc extents left gaps in the extent-state tree.
- Encoded read/write bypass normal buffered data transformation. Misreported compression type, unencoded offset, disk I/O size, or extent length can expose corrupt data, overrun user buffers, or break send/receive and encoded ioctl ABI compatibility.
- Encoded write must reject NODATASUM/NOCOW-incompatible compressed writes and enforce sector alignment. Relaxing these checks can create compressed extents without expected checksums or extents that later read paths cannot decode safely.
- The encoded read endio path relies on refcount memory ordering around `priv->status`. Changes to completion/refcount handling can produce lost I/O errors or premature io_uring completion.
- Swap activation is correctness-critical. Allowing holes, shared/COW extents, compression, checksums, multi-device profiles, device changes, snapshots, or moving block groups while active can lead to swap I/O hitting stale or relocated physical blocks.
- Swap activation locks the entire aligned file range. Empty or sub-sector-sized files need careful treatment by callers because this code computes `isize - 1` after sector alignment.
- Operation table wiring is a broad integration point. A wrong callback assignment can silently change VFS behavior for all Btrfs files or directories.

## Test and Validation Signals

Useful validation should include xfstests and targeted Btrfs scenarios:

- Rename coverage for `RENAME_NOREPLACE`, `RENAME_EXCHANGE`, `RENAME_WHITEOUT`, unsupported flags, and post-rename fsync/sync behavior.
- Snapshot and sync tests that create dirty delalloc across many roots/inodes, then verify `btrfs_start_delalloc_snapshot()` and bounded `btrfs_start_delalloc_roots()` write the expected amount without deadlock under memory reclaim.
- Symlink tests for inline-size boundaries, sector-size boundaries, mount/remount persistence, and failed transaction cleanup.
- Tmpfile tests covering open, linkat of an `O_TMPFILE`, orphan cleanup after crash/recovery, and nlink handling.
- Fallocate/preallocation tests for keep-size and non-keep-size ranges, fragmented allocations, qgroup limits, ENOSPC injection, remount persistence of `i_size`/`disk_i_size`, and relocation races around newly reserved extents.
- Permission tests for readonly roots and `BTRFS_INODE_READONLY` files, directories, and symlinks, with ordinary DAC/ACL checks still delegated to `generic_permission()`.
- Encoded read/write ioctl tests for zlib/lzo/zstd, inline compressed extents, holes, prealloc extents, uncompressed extents, short user buffers returning `-ENOBUFS`, NOWAIT returning `-EAGAIN`, io_uring completion, NODATASUM rejection, alignment rejection, EOF handling, and checksum verification after write completion.
- Send/receive tests that preserve compressed extents through encoded reads and writes.
- Swapfile tests for accepted nocow/nodatasum/single-device files and rejection of compressed, checksummed, holey, inline, shared, reflinked, multi-device, readonly block-group, snapshot-racing, and deleting-subvolume cases.
- Fault-injection tests for allocation failures in path allocation, delalloc work allocation, extent-map creation, compressed folio allocation, qgroup reservation, bio submission, and swap pin allocation.
- Assertion-enabled tests that exercise `btrfs_assert_inode_range_clean()` after flushing and locking ranges.

## Cross-Chunk Notes

This chunk begins immediately after the main rename implementations and only includes the `rename2` dispatcher. The full rename semantics, transaction item counts, inode link updates, and whiteout handling are in earlier chunks.

The final operation tables reference many functions implemented before line 8841 and should be reconciled with those chunks for a complete per-file callback map. Conversely, the encoded I/O helpers and preallocation helpers implemented here are referenced by headers and other Btrfs files, so the merged file report should connect this chunk to `btrfs_inode.h`, `file.c`, `ioctl.c`, and `send.c`.
