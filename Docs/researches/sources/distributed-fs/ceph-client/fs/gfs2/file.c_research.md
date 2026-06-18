## sources/distributed-fs/ceph-client/fs/gfs2/file.c

### Purpose
`file.c` wires GFS2 regular-file and directory VFS operations to the cluster lock, quota, allocation, journaling, iomap, DLM POSIX lock, and DLM flock subsystems. It provides file operation tables for clustered-lock and local-lock mounts and implements the operational path for seek, readdir, mmap faults, open/release, fsync, buffered/direct reads and writes, fallocate, splice write sizing hints, ioctls, file attributes, POSIX locks, and flock locks.

### Important APIs, Types, and Functions
The exported or externally referenced entry points are `gfs2_fileattr_get`, `gfs2_fileattr_set`, `gfs2_set_inode_flags`, `gfs2_open_common`, `gfs2_file_fops`, `gfs2_dir_fops`, `gfs2_file_fops_nolock`, and `gfs2_dir_fops_nolock`. VFS callbacks include `gfs2_llseek`, `gfs2_readdir`, `gfs2_mmap`, `gfs2_open`, `gfs2_release`, `gfs2_fsync`, `gfs2_file_read_iter`, `gfs2_file_write_iter`, `gfs2_fallocate`, `gfs2_lock`, and `gfs2_flock`. The file-private state is `struct gfs2_file` from `incore.h`, primarily used to serialize and remember flock glock holders.

### Control Flow
Read-side operations acquire enough glock state to make cluster-visible inode metadata safe. `SEEK_END` takes the inode glock shared before reading file size, while `SEEK_DATA` and `SEEK_HOLE` delegate to inode helpers that use iomap under the glock. Directory iteration takes the directory glock shared and calls `gfs2_dir_read`. Buffered reads first attempt a no-I/O generic read with page faults disabled, then take the inode glock shared and retry with explicit user-page faulting windows. Direct reads take the inode glock in deferred mode to permit concurrent direct I/O.

Write-side flow is stricter. `gfs2_file_write_iter` records an allocation size hint, refreshes size for append writes, takes `inode_lock`, runs generic write checks and privilege stripping, then routes direct and buffered I/O. Direct writes take a deferred glock and fall back to buffered I/O for extending or page-fault-heavy writes; buffered writes take the inode glock exclusive, optionally lock statfs for rindex writes, and use iomap buffered write ops. `gfs2_page_mkwrite` is the mmap-write allocation path: it takes the inode glock exclusive, updates timestamps, reserves quota and resource-group space, starts a transaction, unstuffs inline data if needed, allocates backing blocks with `gfs2_iomap_alloc`, marks the folio dirty, and releases quota/reservation/glock state on all exits.

`gfs2_fallocate` takes `inode_lock` and an exclusive inode glock, validates mode and size growth, gets write access, and either punches holes externally via `__gfs2_punch_hole` or allocates chunks. Chunk allocation computes quota/rgrp-limited maximum byte ranges, starts transactions with dinode/statfs/quota/rgrp reservations, allocates iomap ranges, and zeroes new blocks with `sb_issue_zeroout`.

### State and Persistence Behavior
The file mutators persist inode flags, timestamps, block mappings, allocation bitmaps, quota changes, statfs changes, and dinode metadata through GFS2 transactions. `do_gfs2_set_flags` handles `FS_IOC_*FLAGS` translation, flushes and truncates data when toggling journaled-data mode, updates `ip->i_diskflags`, writes the dinode, and refreshes inode flags/address-space operations. `gfs2_fsync` writes data first, syncs inode metadata and journaled data as needed, flushes AIL buffers with `gfs2_ail_flush`, and waits on file data ranges. `gfs2_size_hint` updates `ip->i_sizehint` for lower allocation policy.

### Dependencies and Integration Points
This file sits between the Linux VFS/mm/iomap APIs and GFS2 subsystems: `glock.[ch]` for cluster locking, `glops.c` for AIL flush policy, `inode.c` for seek helpers and permission, `bmap`/`aops`/`iomap` for mapping, `rgrp` for allocation, `quota` for accounting, `trans`/`log` for journaling, and DLM `dlm_posix_*` for POSIX byte-range locks. It selects clustered vs local file operation tables through `CONFIG_GFS2_FS_LOCKING_DLM` and `gfs2_localflocks`.

### Risks and Edge Cases
The highest-risk code is around page faults while glocks are held; read/write/direct-I/O paths deliberately disable page faults, drop glocks, fault user pages, and retry. Bugs here can cause partial I/O surprises, deadlocks, or livelock. Fallocate chunk sizing must honor quota and rgrp reservations or it can over-reserve transactions. Flag changes around journaled-data mode require correct writeback, wait, page invalidation, and ordered-list removal. Cluster lock operations must treat withdrawn filesystems as I/O errors and must not sleep while holding `file->f_lock` during flock cleanup.

### Test Signals
Useful signals are xfstests for GFS2 buffered/direct I/O, mmap write faults, append writes from multiple nodes, fallocate and punch-hole behavior, fsync durability in ordered/writeback/jdata modes, fileattr flag transitions, FITRIM/FSLABEL ioctl handling, POSIX lock and flock interoperability through DLM, and fault-injection for user-page faults and allocation/quota failures.
