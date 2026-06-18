# sources/distributed-fs/ceph-client/fs/btrfs/file.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/file.c` implements regular-file operations and file extent mutation for Btrfs. It provides the VFS `file_operations` table, buffered/direct/encoded write dispatch, fsync and tree-log integration, mmap write-fault handling, fallocate/punch-hole/zero-range behavior, SEEK_DATA/SEEK_HOLE, NOCOW write eligibility, file extent dropping/replacement, prealloc-to-written conversion, and helper flows for dirty folio and delayed allocation accounting. The source was read as a complete 3896-line file for this report.

## Important APIs, Types, and Functions

Public functions exported through `file.h` include `btrfs_sync_file()`, `btrfs_drop_extents()`, `btrfs_replace_file_extents()`, `btrfs_mark_extent_written()`, `btrfs_do_write_iter()`, `btrfs_release_file()`, `btrfs_dirty_folio()`, `btrfs_fdatawrite_range()`, `btrfs_check_nocow_lock()`, `btrfs_check_nocow_unlock()`, `btrfs_find_delalloc_in_range()`, `btrfs_write_check()`, and `btrfs_buffered_write()`.

`btrfs_drop_extents()` is the central low-level file extent deletion helper. It walks `BTRFS_EXTENT_DATA_KEY` items for an inode, truncates or splits partially overlapped extents, deletes fully covered items, updates delayed refs and `bytes_found`, optionally leaves an insertion slot for a replacement extent, and reports `drop_end`.

`btrfs_replace_file_extents()` builds on `btrfs_drop_extents()` for hole punching and extent replacement. It starts transactions, reserves metadata, drops existing file extents over a range, inserts explicit holes or replacement extents when needed, updates inode byte accounting, refreshes inode timestamps/version, and returns an open transaction through `trans_out` on success.

`btrfs_mark_extent_written()` converts preallocated extents to regular extents after writes. It may split a prealloc item into leading/written/trailing pieces, merge with adjacent regular extents that reference the same disk extent, and adjust delayed refs for shared extent-item references.

Buffered write helpers include `btrfs_write_check()`, `reserve_space()`, `copy_one_range()`, `btrfs_dirty_folio()`, and `btrfs_buffered_write()`. They perform generic write checks, privilege/time updates, hole expansion, data and metadata reservation, NOCOW fallback, folio preparation, extent locking, ordered-extent waiting, atomic copy from the iterator, delayed allocation marking, and inode size updates.

File operation entry points include `btrfs_file_write_iter()`, `btrfs_file_read_iter()`, `btrfs_file_splice_read()`, `btrfs_file_open()`, `btrfs_file_llseek()`, `btrfs_file_mmap_prepare()`, `btrfs_fallocate()`, and `btrfs_release_file()`. `btrfs_file_operations` wires these into VFS along with ioctl, remap, uring command, lease, and splice helpers.

## Control Flow

The write path enters through `btrfs_do_write_iter()`. It rejects writes after shutdown or filesystem error, disallows NOWAIT encoded writes, and dispatches to encoded, direct, or buffered write handling. Buffered writes take the inode lock, run generic and Btrfs write checks, then loop over `copy_one_range()`. Each iteration faults user pages before locking folios, reserves data/metadata or obtains a NOCOW lock, balances dirty pages, prepares an uptodate mapped folio if partial-block preservation is needed, waits for overlapping ordered extents, copies bytes, marks the range delalloc and folio dirty, releases reservations/locks, and advances `ki_pos`. Direct writes are delegated to `btrfs_direct_write()`, while encoded writes use ioctl encoded I/O arguments and reject partial encoded writes.

The fsync path in `btrfs_sync_file()` always expands the requested range to the whole file. It starts writeback, locks the inode and mmap lock, starts writeback again to close the race with dirty pages created before locking, decides fast versus full sync, waits for ordered extents or writeback as required, and either skips logging if already committed, logs the dentry into the tree log, synchronizes the log, or falls back to a full transaction commit. It carefully drops the inode lock before log sync/commit and, on fast-sync fallback, ends the transaction before waiting for ordered extents to avoid deadlocks with fallocate and transaction commit.

The mmap write-fault path in `btrfs_page_mkwrite()` reserves delalloc space before locking the folio to avoid dirty-page writeback deadlocks. It locks the mmap range, validates EOF/truncation races, waits for ordered extents, marks the page range delalloc, zeroes bytes beyond EOF inside the folio, marks Btrfs folio state dirty/uptodate, updates last-subtransaction state, and returns `VM_FAULT_LOCKED` with the folio locked for the VM.

Hole punching in `btrfs_punch_hole()` locks the inode/mmap state, waits for ordered extents, skips existing holes, zeroes unaligned boundary blocks through `btrfs_truncate_block()`, locks and truncates page cache for the aligned interior through `btrfs_punch_hole_lock_range()`, calls `btrfs_replace_file_extents()` with no replacement info, updates inode metadata, and unlocks the extent range. `btrfs_zero_range()` and `btrfs_fallocate()` share the same primitives but allocate preallocated extents for holes or zero ranges, reserve qgroup/data space, and update i_size when `KEEP_SIZE` is not set.

SEEK_DATA/SEEK_HOLE enters through `btrfs_file_llseek()` and `find_desired_extent()`. It locks the inode shared, searches file extent items, treats prealloc and disk_bytenr-zero regular extents as holes, detects implicit holes between extent items, overlays delalloc and ordered extents through `btrfs_find_delalloc_in_range()`, and returns either the next data offset, hole offset, i_size, or `-ENXIO`.

## State and Persistence Behavior

Persistent state includes file extent items, extent reference counts, explicit hole items, preallocated and written extent types, inode item timestamps/version/size, and tree-log entries. Mutating paths run inside Btrfs transactions and often abort the transaction if an operation would leave dropped extents without the required replacement or hole item. `btrfs_replace_file_extents()` deliberately reopens transactions over long ranges to balance dirty B-tree pages and preserve crash consistency across partial progress.

Runtime state includes folio dirty/uptodate/checked bits, inode `io_tree` flags (`EXTENT_DELALLOC`, `EXTENT_NORESERVE`, `EXTENT_DEFRAG`, and ordered extent ranges), delayed allocation reservation state, qgroup reservation changesets, extent maps, `file->private_data` llseek cache state, log context ordered-extents lists, and `BTRFS_INODE_*` runtime flags such as `NEEDS_FULL_SYNC`, `COW_WRITE_ERROR`, `FLUSH_ON_CLOSE`, and `NO_DELALLOC_FLUSH`.

`disk_i_size` and file extent range tracking are coordinated with helpers from `file-item.c`. For filesystems without `NO_HOLES`, explicit hole items and the in-memory `file_extent_tree` keep the durable size from advancing across gaps. For fast fsync correctness, replacement/cloning paths may force full sync if extent maps were dropped or holes are only implicit.

## Dependencies and Integration Points

This file integrates Linux VFS file operations, page cache/folios, mmap fault handling, writeback, direct I/O, splice, fallocate modes, fsverity open checks, and generic write/llseek helpers. Btrfs dependencies include transactions, tree-log logging/sync, ordered extents, delalloc reservation, qgroups, compression writeback behavior, NOCOW/prealloc extent checks, extent-tree reference helpers, reflink/remap operations, ioctl encoded writes, subpage folio state, root snapshot locks, inode locks, and extent maps.

Important external callers include inode writeback/inline extent creation via `btrfs_drop_extents()`, reflink cloning through `btrfs_replace_file_extents()`, encoded write ioctls through `btrfs_do_write_iter()`, and tree-log code that relies on fsync ordering and checksum/extent consistency. The exported `btrfs_file_operations` is the VFS integration point for normal file descriptors.

## Risks and Edge Cases

The highest-risk areas are transaction error handling after partial extent deletion, delayed-ref accounting while splitting or merging extents, lock ordering between inode locks, mmap locks, extent locks, ordered extents, and transactions, and reservation unwinding on short copies or NOWAIT failures. Inline extents often return `-EOPNOTSUPP` for operations that require splitting; callers must distinguish clone limitations from corruption-worthy failures.

Fsync has many subtle races: dirty pages created before inode locking, ordered extent completion that updates file extent items and checksums, COW write errors that require waiting and dropping bad extent maps, zoned writes whose logical address stabilizes only after I/O, and fast-sync log checksum overlap after reflink. SEEK_DATA/SEEK_HOLE must combine on-disk extents, implicit holes, explicit hole items, prealloc extents, delalloc, and ordered extents without returning stale cached state from another task.

Fallocate and punch-hole edge cases include unaligned boundaries, large folios that partially overlap the lock range, subpage sectors, holes beyond EOF, `NO_HOLES` filesystems, qgroup limits, zoned filesystem rejection, and crash consistency when a long range requires multiple transactions.

## Test Signals

Useful signals include xfstests for buffered writes, direct writes, NOWAIT writes, NOCOW and prealloc writes, encoded writes, mmap write faults, fsync after buffered/direct/reflink writes, log replay after fast fsync, fallocate preallocation, zero range, punch hole with unaligned boundaries, `NO_HOLES` versus explicit holes, SEEK_DATA/SEEK_HOLE with delalloc and ordered extents, truncate/clone interactions, qgroup ENOSPC, zoned fallocate rejection, compression writeback fsync behavior, subpage and large-folio page-cache cases, and fault injection for ENOMEM/ENOSPC/EIO in extent mutation and reservation unwinding.
