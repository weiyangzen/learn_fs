# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc.h

Purpose: Public header for classic HFS relocation helpers.

Exports: `hfs_update_mdb(PedFileSystem *fs)` and `hfs_pack_free_space_from_block(PedFileSystem *fs, unsigned int fblock, PedTimer *timer, unsigned int to_free)`.

Dependencies: Includes libparted core, endian/debug headers, and `hfs.h`.

Important details and risks: The header exposes only the MDB update and pack operation; all cache-building and low-level extent movement remain private to `reloc.c`. Callers need a fully initialized HFS `PedFileSystem` with valid private data and allocation map.
