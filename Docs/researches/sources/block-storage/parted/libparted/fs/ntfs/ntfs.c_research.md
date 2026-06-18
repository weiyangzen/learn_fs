# File Research: sources/block-storage/parted/libparted/fs/ntfs/ntfs.c

Minimal NTFS probe module. `ntfs_probe()` reads the first sector of the candidate geometry, checks for the `"NTFS"` signature at byte offset 3, then copies the 64-bit total-sector count from offset `0x28` and returns a geometry of that length from the input start.

The code does not endian-convert the copied length explicitly, relying on little-endian host behavior or compatible representation. It also does not validate bytes-per-sector, sectors-per-cluster, MFT fields, or boot-sector checksum. The module registers a single filesystem type named `ntfs`.
