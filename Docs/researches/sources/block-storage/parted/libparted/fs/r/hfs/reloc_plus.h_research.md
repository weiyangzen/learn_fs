# File Research: sources/block-storage/parted/libparted/fs/r/hfs/reloc_plus.h

Purpose: Public header for HFS+ relocation helpers.

Exports: `hfsplus_update_vh(PedFileSystem *fs)` and `hfsplus_pack_free_space_from_block(PedFileSystem *fs, unsigned int fblock, PedTimer *timer, unsigned int to_free)`.

Dependencies: Includes libparted core, endian/debug headers, and `hfs.h`.

Important details and risks: The API assumes HFS+ private data, `plus_geom`, volume header, open metadata files, and allocation maps are already initialized by the HFS+ resize stack.
