# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs_types.h

Purpose: Imported XFS core type definitions used by `xfs_sb.h`.

Content: Defines allocation group, extent, filesystem block, realtime block, file offset, transaction/log, directory/hash, project ID, null sentinel, max extent constants, lookup and btree enums, optional statistics macros, and kernel-only IRIX device helpers.

Dependencies: Requires fixed-width integer types and is shaped by `XFS_BIG_FILES` and `XFS_BIG_FILESYSTEMS`, both enabled here.

Important details and risks: For libparted’s XFS probe, this header mainly ensures the superblock structure has the expected field widths. Much of the statistics and kernel-only material is unused in this tree. Reuse outside the probe should account for the age of these definitions relative to modern XFS.
