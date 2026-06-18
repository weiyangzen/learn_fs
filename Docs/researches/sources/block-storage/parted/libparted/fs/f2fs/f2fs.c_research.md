# File Research: sources/block-storage/parted/libparted/fs/f2fs/f2fs.c

Minimal f2fs probe module. `f2fs_probe()` allocates one device sector on the stack, reads sector offset `F2FS_SB_OFFSET` from the geometry, and checks the little-endian `F2FS_MAGIC`.

On success it returns a new geometry covering the entire input geometry. The module registers one filesystem type named `f2fs` and unregisters it in the matching done function.

The probe does not validate checksum, block size fields, segment layout, or backup superblock. It is a simple signature detector using the packed superblock prefix defined in `f2fs.h`.
