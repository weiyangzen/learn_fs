# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs.c

Purpose: Detection-only XFS filesystem backend.

Main interfaces: Registers a `PedFileSystemType` named `xfs` with probe operation `xfs_probe()`.

Control flow: `xfs_probe()` reads the superblock at `XFS_SB_DADDR` and checks `sb_magicnum` against `XFS_SB_MAGIC` in little-endian and big-endian forms. On match, it derives filesystem length from `sb_blocksize / sector_size * sb_dblocks` and returns a new geometry.

Dependencies: Uses libparted geometry/endian APIs, UUID headers, and imported `platform_defs.h`, `xfs_types.h`, and `xfs_sb.h`.

Important details and risks: XFS on disk is normally big-endian, but this code accepts both endian interpretations. It does not validate superblock version, sector size, UUID, AG geometry, or checksums. Tests should include valid big-endian XFS, bogus magic, too-short geometry, and corrupted block-size/count fields.
