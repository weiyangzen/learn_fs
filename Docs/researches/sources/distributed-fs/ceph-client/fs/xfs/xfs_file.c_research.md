# sources/distributed-fs/ceph-client/fs/xfs/xfs_file.c

## Purpose
`xfs_file.c` is the VFS file operation layer for XFS regular files and directories. It implements reads, writes, DAX faults, fsync, fallocate, reflink remap, directory reads, open/release heuristics, mmap setup, and file operation tables.

## Important APIs, types, and functions
Exported objects are `xfs_file_operations` and `xfs_dir_file_operations`; exported helper `xfs_is_falloc_aligned` checks allocation-unit alignment. Important flows are `xfs_file_read_iter`, `xfs_file_write_iter`, `xfs_file_fsync`, `xfs_file_fallocate`, `xfs_file_remap_range`, `xfs_file_open`, `xfs_file_release`, `xfs_file_llseek`, and `xfs_file_mmap_prepare`. Internal helpers separate buffered, DIO, DAX, zoned, unaligned, and atomic write paths, EOF zeroing, direct-I/O completion, mmap write faults, and fallocate modes.

## Control flow
Reads reject shutdown mounts, update stats, and dispatch to DAX, direct, buffered, or splice paths under `XFS_IOLOCK_SHARED`. Writes validate atomic constraints, choose DAX/direct/buffered/zoned paths, and use `xfs_file_write_checks` for generic limits, layout breakage, privilege removal needs, and post-EOF zeroing. Direct I/O enforces device-sector alignment, routes unaligned writes through overwrite-only/exclusive retry logic, routes zoned writes through space reservation and zone allocation, and routes atomic writes through hardware atomic or CoW fallback. DIO completion updates stats, completes CoW or unwritten conversion, and serializes EOF updates. Buffered writes retry once after quota/space cleanup. Fallocate takes IO/MMAP exclusive locks, drains DIO, calls file modification checks, and dispatches punch, collapse, insert, zero, unshare, or allocate-range helpers. Reflink remap uses reflink prep/remap/update helpers and syncs if either file requires it. Mmap faults use DAX or iomap page-mkwrite under MMAPLOCK and pagefault freeze protection.

## State and persistence
Persistent effects include file data writes, extent conversion, CoW completion, inode size updates, timestamp/security privilege changes, fallocate extent edits, reflink sharing, and log/device flushes for sync operations. Runtime state includes IO/MMAP lock modes, `XFS_ITRUNCATED` and `XFS_EOFBLOCKS_RELEASED`, zoned allocation contexts, DIO completion flags, i_size serialization with `i_flags_lock`, and stats counters. Release may flush delayed blocks after truncation and opportunistically free post-EOF preallocations.

## Dependencies and integration points
The file integrates VFS `file_operations`, iomap buffered/direct/DAX APIs, XFS iomap ops, reflink, CoW, zoned allocator, block device flushes, writeback, file leases, fadvise, directory readdir, ioctl handlers, pNFS, transparent hugepage unmapped-area helper, and trace/stats/error tags.

## Risks and test signals
Risks include IOLOCK demotion/upgrade races, unaligned direct-I/O zeroing corruption, EOF moving backward under AIO completion, DAX synchronous fault handling, zoned reservation accounting, atomic write fallback correctness, buffered write retry behavior under ENOSPC/EDQUOT, post-EOF preallocation heuristics, and fsync ordering across data/log/realtime devices. Test signals include NOWAIT read/write, DAX read/write/faults, direct unaligned writes to reflink files, atomic writes over one and multiple extents, zoned buffered and direct writes, fallocate all modes, collapse/insert alignment failures, remap partial results, fsync with separate log/rt devices, last-close EOF block cleanup, SEEK_DATA/SEEK_HOLE, and mmap write faults during remap/truncate.
