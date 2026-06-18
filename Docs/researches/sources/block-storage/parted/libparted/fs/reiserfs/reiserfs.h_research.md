# File Research: sources/block-storage/parted/libparted/fs/reiserfs/reiserfs.h

Purpose: Minimal ReiserFS on-disk definitions used by libparted probing.

Content: Defines ReiserFS magic strings, default block size, `struct reiserfs_super_block`, exception/gauge compatibility typedefs, format constants, journal constants, and hash identifiers.

Dependencies: Relies on fixed-width integer types being available from including translation units.

Important details and risks: Most declarations are compatibility leftovers and are not consumed by current `reiserfs.c`; the active probe depends primarily on `s_block_count`, `s_blocksize`, and `s_magic`. The struct layout must remain aligned with the on-disk superblock fields used by old ReiserFS formats.
