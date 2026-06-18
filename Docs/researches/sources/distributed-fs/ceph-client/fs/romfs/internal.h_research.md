# sources/distributed-fs/ceph-client/fs/romfs/internal.h

## Purpose
`internal.h` defines ROMFS-private inode metadata, helpers, and cross-file declarations for storage access and optional NOMMU MTD file operations.

## Important APIs, Types, And Functions
`struct romfs_inode_info` embeds `struct inode` and adds `i_metasize` for non-data bytes plus `i_dataoffset` from filesystem start. `romfs_maxsize()` interprets `sb->s_fs_info` as the maximum accessible filesystem size. `ROMFS_I()` converts a VFS inode to the ROMFS inode wrapper.

The header conditionally declares `extern const struct file_operations romfs_ro_fops` for `!CONFIG_MMU && CONFIG_ROMFS_ON_MTD`; otherwise it aliases `romfs_ro_fops` to `generic_ro_fops`. Storage APIs exported from `storage.c` are `romfs_dev_read()`, `romfs_dev_strnlen()`, and `romfs_dev_strcmp()`.

## Control Flow
The only control flow is preprocessor selection of file operations. NOMMU MTD builds use ROMFS-specific operations that can request direct MTD mappings. All other builds use generic read-only file operations.

## State And Persistence
ROMFS inode state lives in allocated inodes managed by `super.c`. `i_dataoffset` and `i_metasize` persist in memory for each inode after parsing on-disk metadata. Superblock `s_fs_info` carries image-size information consumed by storage bounds checks.

## Dependencies And Integration Points
The header includes `linux/romfs_fs.h` for format constants such as ROMFS limits. It integrates storage helpers with superblock/inode parsing and maps file operations to `mmap-nommu.c` when configured.

## Risks
`romfs_maxsize()` relies on `s_fs_info` being initialized to a valid size-compatible pointer value by mount code. Wrong `i_dataoffset` values can make storage and mmap code read or map the wrong image area. The file-operations conditional must match the Makefile conditional.

## Test Signals
Tests should verify inode wrapper conversion, max-size initialization during mount, correct use of generic file ops on MMU or non-MTD builds, and use of `romfs_ro_fops` on NOMMU MTD builds.
