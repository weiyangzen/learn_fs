# sources/distributed-fs/ceph-client/fs/fat/inode.c

## Purpose
`inode.c` is the FAT core mount, inode, address-space, writeback, option parsing, and module lifecycle implementation. It reads the boot sector/BPB, builds in-core superblock geometry, initializes NLS and special inodes, maps file IO to cluster allocation, and writes inode metadata back into directory entries.

## Important APIs, Types, and Functions
- `fat_add_cluster()`, `__fat_get_block()`, and `fat_get_block()` bridge pagecache block mapping to FAT cluster allocation.
- `fat_aops` defines FAT address-space behavior for read, readahead, writepages, write_begin/end, direct IO, bmap, and migration.
- `fat_attach()`, `fat_detach()`, and `fat_iget()` maintain the directory-entry-position inode hash; directory hash support backs NFS reconnect.
- `fat_fill_inode()`, `fat_build_inode()`, and `fat_read_root()` construct VFS inodes from on-disk directory entries or root geometry.
- `fat_write_inode()` / `__fat_write_inode()` persist inode size, attributes, start cluster, and timestamps to the directory entry.
- `fat_parse_param()`, `fat_init_fs_context()`, `fat_free_fc()`, and `fat_reconfigure()` manage mount options.
- `fat_fill_super()` performs full mount setup and validation.

## Control Flow
Mount begins with `fat_init_fs_context()` defaults in the msdos/vfat module, option parsing through `fat_parse_param()`, and block-device mounting through `fat_fill_super()`. `fat_fill_super()` allocates `msdos_sb_info`, sets VFS superblock operations, reads the boot sector, validates the BPB or optional DOS 1.x defaults, computes FAT/root/data layout, detects FAT type, loads NLS tables, creates the FAT and FSINFO pseudo-inodes, reads the root inode, attaches hashes, and marks the volume dirty.

File IO mapping starts in `fat_get_block()`. If an existing mapping is found, it returns a mapped buffer. For writes at `mmu_private`, it allocates a new cluster when needed, advances `mmu_private`, remaps, marks new buffers, and reports corruption if mapping still fails. Inode writeback reads the directory entry block from `i_pos`, verifies under `inode_hash_lock` that the inode still owns that position, then writes size, attrs, start cluster, mtime/date, and VFAT atime/crtime fields.

## State and Persistence
Persistent state includes the boot-sector dirty bit, BPB-derived layout, FSINFO counters, FAT table through dependencies, root and directory entries, and file data clusters. In-core state includes inode caches, two hash tables, mount options, NLS tables, `free_clusters`, `prev_free`, special inodes, and metadata buffer ledgers. `fat_set_state()` marks the volume dirty on mount/remount writable and clean on unmount/remount read-only when appropriate.

## Dependencies and Integration Points
This file ties together nearly every FAT subsystem: `cache.c` for mapping, `fatent.c` for FAT access, `dir.c` for root/subdir sizing and link counts, `file.c` for inode operations, `misc.c` for timestamps/errors, and `nfs.c` export operations. It uses VFS fs_context, superblock, address-space, inode cache, mpage, direct IO, buffer-head, block-device, NLS, random generation, and idmapped mount APIs.

## Risks and Test Signals
Mount validation must reject malformed BPBs while tolerating real-world oddities. FAT32 FSINFO may be invalid or stale. Inode identity is complex because `i_ino` is synthetic while persistence is tied to `i_pos`; rename/unlink races are handled by detach/attach and writeback revalidation. Tests should cover FAT12/16/32 mounts, invalid BPBs, dirty-bit behavior, FSINFO counters, remounts, NFS options, buffered writes, direct IO fallback, truncate, bmap, and writeback after rename/unlink.
