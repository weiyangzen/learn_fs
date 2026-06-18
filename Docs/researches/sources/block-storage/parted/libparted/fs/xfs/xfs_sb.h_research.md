# File Research: sources/block-storage/parted/libparted/fs/xfs/xfs_sb.h

Purpose: Imported XFS superblock definitions and version/feature macros used by the XFS probe and potentially by older XFS utility code.

Content: Defines `XFS_SB_MAGIC`, version constants, feature-bit masks, `xfs_sb_t` layout, field-number enum, superblock field bit masks, feature test/add/subtract macros, and block/basic-block/byte conversion macros.

Dependencies: Depends on XFS integer types from `xfs_types.h`, `uuid_t`, and optional `XFS_WANT_FUNCS`/`XFS_WANT_SPACE` macro regimes.

Important details and risks: The active libparted probe uses only the superblock struct, magic, blocksize, and dblocks. Many macros are legacy imported logic and are not compiled into functions unless external feature macros request it. The header represents an older XFS format generation and should not be treated as a complete modern XFS feature model.
