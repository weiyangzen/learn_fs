# sources/distributed-fs/ceph-client/fs/hpfs/file.c

Purpose: this file implements HPFS regular-file VFS operations, page-cache block mapping, writeback, truncate, fsync, and fiemap.

Important APIs and functions: `hpfs_bmap()` maps file sectors through the fnode/anode allocation tree, using inode extent cache. `hpfs_get_block()` is the buffer-head mapper for mpage read/write and block bmap. `hpfs_truncate()` truncates allocation trees and writes inode metadata. `hpfs_iomap_begin()` supports read-only fiemap. `hpfs_write_begin()`/`hpfs_write_end()` integrate generic buffered writes with allocation and dirty metadata. `hpfs_file_ops`, `hpfs_file_iops`, and `hpfs_aops` expose VFS behavior.

Control flow: reads and readahead call mpage helpers with `hpfs_get_block()`. Existing mappings use `hpfs_bmap()`, hotfix clipping, and `map_bh()`. Write allocation is only allowed exactly at `mmu_private`, enforcing contiguous logical file extension. New sectors are added via `hpfs_add_sector_to_btree()`, inode block count and `mmu_private` are advanced, and the buffer is marked new. Write-end marks the inode dirty so close/release writes metadata. Fiemap uses iomap on existing mappings only.

State and persistence: data sectors are allocated/freed through allocation B+ trees and bitmaps. Inode size, `i_blocks`, `mmu_private`, cached extent fields, and dirty state are mutated. Fsync flushes page-cache writes and synchronizes the block device.

Dependencies and integration: it depends on `anode.c`, `alloc.c`, `buffer.c` hotfix helpers, `inode.c` metadata writing, Linux mpage/iomap/fiemap APIs, and global HPFS locking.

Risks: the write path rejects non-EOF block allocation with `BUG()`; correctness depends on generic buffered write sequencing and `mmu_private`. Write failures must truncate page cache and allocation back to inode size. Fiemap is read-only and rejects write/zero iomap flags. Hotfixes can reduce contiguous mapping lengths.

Test signals: buffered reads/writes, append growth sector by sector, fragmented allocation, write failure cleanup, truncate shrink, fsync after data/metadata updates, fiemap over mapped and hole ranges, bmap around EOF, hotfix range clipping, and close-triggered metadata writeback.
