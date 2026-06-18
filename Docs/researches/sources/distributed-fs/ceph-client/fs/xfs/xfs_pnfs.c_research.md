# sources/distributed-fs/ceph-client/fs/xfs/xfs_pnfs.c

Purpose: Implements XFS support for NFS pNFS block layouts, including layout recall synchronization, filesystem UUID export, block mapping for clients, preallocation and durability for write layouts, and commit handling after clients write directly to storage.

Important APIs, types, and functions: `xfs_break_leased_layouts` recalls outstanding layouts before local operations remove blocks or need synchronization. `xfs_fs_get_uuid` returns the filesystem UUID and its on-disk superblock offset. `xfs_fs_map_blocks` maps file byte ranges to `struct iomap` for pNFS clients, allocating blocks for write layouts when needed. `xfs_fs_commit_blocks` converts unwritten extents, invalidates page cache, updates timestamps/size, and commits synchronously. Internal helpers `xfs_fs_map_update_inode` and `xfs_pnfs_validate_isize` handle inode metadata updates and size validation.

Control flow: Mapping rejects shutdown, realtime inodes, and reflink inodes. It takes `XFS_IOLOCK_EXCL`, bounds the request, flushes and invalidates page cache, reads the data fork map, and for write holes allocates direct I/O blocks, marks the inode preallocated, commits metadata, and forces the inode log before returning an iomap with the mount generation. Commit takes the IOLOCK, invalidates affected pagecache ranges, converts unwritten extents, validates any size extension points into allocated written space, then logs inode timestamps and size in a synchronous transaction.

State and persistence behavior: Can allocate blocks, set `XFS_DIFLAG_PREALLOC`, strip SUID/SGID, update ctime/mtime/atime, update `i_size` and `i_disk_size`, convert unwritten extents, and force log durability so handed-out pNFS layouts survive server crashes. It returns `m_generation` so clients can detect layout changes after growfs.

Dependencies and integration points: Integrates XFS bmap/iomap, transactions, inode locks, pagecache writeback/invalidation, VFS lease layout breaking, exportfs block operations, log force, and mount generation. It is conditionally exposed by `xfs_pnfs.h` under `CONFIG_EXPORTFS_BLOCK_OPS`.

Risks: Layout handing out block addresses is sensitive to stale page cache, delayed allocations, unwritten extents, reflink sharing, realtime-device identity, and crash durability. The code intentionally avoids pNFS for reflink and realtime files. Size extension must not expose holes or unwritten extents as valid EOF. Lock dropping in layout breaking changes IOLOCK mode and must be reflected to callers.

Test signals: Exercise read and write pNFS layouts, holes requiring allocation, EOF extension, unwritten extent conversion, SUID/SGID stripping, pagecache invalidation failures, shutdown, reflink and realtime rejection, layout recall returning `-EWOULDBLOCK`, and growfs generation changes. Crash tests should verify allocated write-layout blocks remain mapped after recovery.
