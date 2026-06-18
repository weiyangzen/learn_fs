<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/inode.c -->
# sources/distributed-fs/ceph-client/fs/minix/inode.c

## Purpose
`inode.c` is the Minix filesystem superblock, inode, address-space, and module registration implementation. It mounts V1/V2/V3 Minix block devices, validates their static layout, reads bitmap blocks, creates the root dentry, selects V1 versus V2 inode formats, wires inode operation tables, and implements inode writeback, eviction, truncation dispatch, statfs, getattr, and page-cache block I/O glue.

## Important APIs, Types, and Functions
Key exported/internal entry points are `minix_iget()`, `minix_set_inode()`, `minix_truncate()`, `minix_getattr()`, `minix_prepare_chunk()`, and the module `minix_fs_type`. `minix_fill_super()` is the mount-time core. It populates `struct minix_sb_info`, identifies Minix V1/V2/V3 magic values and directory name lengths, reads inode and zone bitmaps, sets `s_op`, loads `MINIX_ROOT_INO`, and builds `s_root`. `minix_reconfigure()` handles remount read-only/read-write transitions. `V1_minix_iget()` and `V2_minix_iget()` decode on-disk inode formats into VFS inodes; `V1_minix_update_inode()` and `V2_minix_update_inode()` write them back. `minix_get_block()` dispatches to `V1_minix_get_block()` or `V2_minix_get_block()` from the indirect-tree implementations. `minix_aops` binds Minix files to buffered I/O helpers such as `block_read_full_folio()`, `mpage_writepages()`, `block_write_begin()`, `generic_write_end()`, and `generic_block_bmap()`.

## Control Flow
Mount starts at `minix_init_fs_context()`, then `get_tree_bdev()` calls `minix_fill_super()`. The fill path fixes an initial block size, reads block 1 as the superblock, recognizes the Minix version, validates bitmap capacity and zone constraints with `minix_check_superblock()`, reads bitmap blocks, reserves bit zero, installs super operations, and loads the root inode. Normal inode lookup uses `iget_locked()` then version-specific raw-inode readers. File I/O routes VFS page-cache operations through `minix_get_block()`, which invokes the V1/V2 indirect mapping code. Eviction truncates unlinked files before freeing their inode bitmap entry, while linked inodes sync and invalidate metadata buffer tracking.

## State and Persistence Behavior
Persistent state lives in the on-disk superblock, inode/zone bitmaps, raw inode tables, and data/indirect blocks. For writable non-V3 mounts, `s_state` is cleared on mount/remount-rw and restored on unmount/remount-ro to record clean versus dirty filesystem state. Inode writeback converts kernel uid/gid/timestamps/link counts/size and zone arrays into the V1 or V2 disk format and marks the raw inode buffer dirty; synchronous writeback explicitly calls `sync_dirty_buffer()`. `minix_evict_inode()` integrates pagecache truncation, indirect-block freeing, metadata-buffer sync via `mmb_sync()`, and inode bitmap freeing.

## Dependencies and Integration Points
This file integrates with `minix.h`, bitmap allocation helpers in other Minix files, VFS superblock/inode/address-space operations, buffer heads, block device mounting, `mpage`, writeback control, and fs-context mounting. The VFS calls `minix_dir_inode_operations`, `minix_file_inode_operations`, `minix_dir_operations`, and `minix_file_operations` declared elsewhere. Idmapped mounts are effectively ignored for getattr by passing `&nop_mnt_idmap` to `generic_fillattr()`, matching Minix's legacy on-disk ownership handling.

## Risks
Mount safety depends on superblock validation; unsupported non-zero `s_log_zone_size`, too-small bitmap tables, invalid first data zone, and V1 maximum-size overflow are rejected. The code uses old device encoding for special files and high-to-low uid/gid conversion, so ownership/device fidelity is limited by the Minix format. Error unwinding in `minix_fill_super()` must release all bitmap and superblock buffers correctly. Any mismatch between `s_version`, inode layout, and indirect-tree dispatch can corrupt block pointers. `minix_write_failed()` must truncate partially allocated blocks after failed writes to avoid stale allocation.

## Test Signals
Useful signals include successful mount/read-only remount/read-write remount/unmount across Minix V1, V2, and V3 images; fsck state changes on writable mounts; root inode lookup failures on corrupt images; `statfs` free block/inode counts; create/write/truncate/fsync/readback tests; special-file and symlink creation; block-size handling for V3; and fault injection around bitmap reads, raw inode reads, synchronous inode writeback, and ENOSPC paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/minix/inode.c -->
