# sources/distributed-fs/ceph-client/fs/btrfs/reflink.c

## Purpose

`sources/distributed-fs/ceph-client/fs/btrfs/reflink.c` implements Btrfs support for VFS `remap_file_range`: clone/reflink and dedupe. It validates remap requests, locks inodes and mmap/range state, flushes ordered extents, clones file extent items or inline data, handles holes and EOF extension, updates inode metadata and fsync state, invalidates stale page cache, and performs synchronous writes when requested. The source was read as a complete 975-line file.

## Important APIs, Types, and Functions

The public API is `btrfs_remap_file_range()`. Internal helpers include `btrfs_remap_file_range_prep()` for Btrfs-specific validation and writeback ordering; `btrfs_clone_files()` for non-dedupe reflink; `btrfs_extent_same()` and `btrfs_extent_same_range()` for dedupe; `btrfs_clone()` for walking source file extents and replacing destination extents; `clone_copy_inline_extent()` and `copy_inline_to_page()` for inline extent handling; `clone_finish_inode_update()` for i_version, timestamps, size, and inode item update; `btrfs_double_mmap_lock()` and unlock counterpart for ordered mmap locking; and `file_sync_write()` for sync semantics.

## Control Flow

`btrfs_remap_file_range()` rejects shutdown and unsupported flags, locks one or both inodes plus mmap locks, calls `btrfs_remap_file_range_prep()`, then dispatches to dedupe or clone. Preparation checks readonly destination rules, encryption compatibility, NODATASUM compatibility, flushes source NOCOW buffered writes, waits for ordered extents on source and destination aligned ranges, and then delegates generic VFS validation.

For clone, `btrfs_clone_files()` expands destination holes if `destoff` is past EOF, waits for writeback around a possibly truncated EOF block, locks the destination extent range, and calls `btrfs_clone()`. `btrfs_clone()` walks source extent items from `off` to `off + aligned_len`, handles overlap with the first extent, skips extents already processed due to races with ordered completion, maps source offsets to destination offsets, drops implicit destination holes, and either calls `btrfs_replace_file_extents()` for regular/prealloc extents or `clone_copy_inline_extent()` for inline extents. After each replacement it updates `last_reflink_trans` as needed for fsync correctness, finishes inode updates in a transaction, and reschedules between iterations. At the end it punches/replaces trailing implicit holes if the clone range extends beyond the last found extent.

Inline extents are special. If they cannot be represented as a destination inline extent, `copy_inline_to_page()` reserves delalloc, creates and dirties a folio, decompresses inline data when required, zero-fills the rest of the sector, and marks the inode as temporarily not flushable for delalloc to avoid deadlocks. `clone_copy_inline_extent()` chooses between inserting an inline item at offset zero and copying into page cache, then opens a transaction only after releasing tree paths and performing reservations that could flush.

For dedupe, `btrfs_extent_same()` increments a destination root `dedupe_in_progress` counter unless send is active, chunks the request into at most `BTRFS_MAX_DEDUPE_LEN` ranges, and calls `btrfs_extent_same_range()` for each. The range helper locks the destination extent range and calls `btrfs_clone()` with `no_time_update=true`.

## State and Persistence Behavior

Persistent effects are changes to destination file extent items, inode size, inode timestamps for clone, inode version, inode bytes, and fsync tracking state. Shared extents increase reference counts via `btrfs_replace_file_extents()` rather than copying data. Inline-data fallbacks may create delalloc dirty folios that are later flushed into regular extents. The code updates `last_reflink_trans` for source and destination to force correct checksum logging during fsync when extent items share subranges of physical extents.

Transient state includes tree paths, extent locks, mmap locks, transaction handles, delalloc reservations, temporary node-sized buffers, cached extent state, and root `dedupe_in_progress` counters. `BTRFS_INODE_NO_DELALLOC_FLUSH` is set around inline-copy paths to avoid a deadlock and cleared on exit from `btrfs_clone()`.

## Dependencies and Integration Points

The file depends on VFS remap helpers and inode locking, fscrypt/encryption state, Btrfs transaction handling, extent and file item manipulation, delalloc reservation/accounting, ordered extent waiting, compression/decompression, page cache invalidation, inode update routines, send/dedupe coordination, root readonly checks, and sync-file handling. It is the implementation behind the prototype in `reflink.h` and is called from Btrfs file operations.

## Risks and Edge Cases

Deadlock avoidance is a major concern: paths release B-tree paths before starting transactions or doing reservations, flush ordered extents before cloning, lock mmap state in a stable order, and temporarily suppress delalloc flushing for inline copies. Inline extents have strict offset and size assumptions; compressed inline data must decompress into the correct folio range and zero-fill the rest of the sector. Hole handling must account for NO_HOLES files and implicit holes at the beginning or end of ranges.

Correctness also depends on alignment. The code rounds clone lengths to sectors at EOF but preserves the user's original length for final i_size updates. Dedupe is chunked to 16 MiB to limit work per range. It rejects encryption mismatches and NODATASUM mismatches to avoid incompatible sharing. Send in progress prevents dedupe into a root. After clone, page cache invalidation can fail if dirty folios remain, so the code waits for ordered ranges before invalidation.

## Test Signals

Relevant fstests include clone and dedupe across holes, inline extents, compressed inline extents, EOF-unaligned files, same-inode remaps, readonly roots, encrypted files, NODATASUM mismatches, send-in-progress roots, sync-file semantics, and concurrent mmap/read/write workloads. Signals include transaction aborts, `-EAGAIN` during send, `-EINVAL` validation failures, page-cache invalidation failures, fsync correctness after shared extents, and lockdep coverage for inode/mmap/extent lock ordering.
