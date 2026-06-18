# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs_superblock.h

JFS aggregate superblock layout header imported from IBM JFS utilities. It defines `JFS_MAGIC`, `JFS_VERSION`, volume-name size, and `struct superblock` when `_JFS_UTILITY` is defined.

The structure includes magic/version, aggregate size and block-size fields, physical block-size fields, allocation group size, flags/state/compression, primary/secondary inode table/map extents, log/fsck extents, update time, fsck log metadata, volume name, extendfs parameters, VFS/reserved fields, and free-space accounting.

The probe uses only `s_magic`, `s_pbsize`, and `s_size`, but the full layout preserves offsets for those fields and supports possible utility reuse.
