# sources/distributed-fs/ceph-client/fs/ramfs/file-mmu.c

Purpose: Supplies ramfs regular-file operations for MMU systems by composing generic page-cache based VFS helpers.

Important APIs, types, and functions: Defines `ramfs_mmu_get_unmapped_area()`, `ramfs_file_operations`, and `ramfs_file_inode_operations`. File operations include generic read/write iterators, mmap preparation, splice read/write, noop fsync, llseek, and get-unmapped-area.

Control flow: Regular-file inodes created by `ramfs_get_inode()` receive these operation tables. Reads, writes, mmap, splice, fsync, and seek are delegated almost entirely to generic VFS/page-cache helpers. The local unmapped-area wrapper calls `mm_get_unmapped_area()`.

State and persistence: ramfs persists file data only in page cache and marks mappings unevictable in `inode.c`; this file adds no private state. `noop_fsync` reflects the lack of backing storage.

Dependencies and integration points: Depends on the MMU memory-management path, generic file helpers, and ramfs inode setup. It is selected by Kbuild when `CONFIG_MMU` is enabled.

Risks and test signals: Risks are mostly integration regressions with generic mmap/read/write helpers and address selection. Test regular file read/write, shared/private mmap, splice, lseek, truncate through setattr, and fsync no-op behavior on ramfs.
