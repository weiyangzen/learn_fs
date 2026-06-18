# File Research: sources/block-storage/parted/libparted/fs/btrfs/btrfs.c

Minimal btrfs probe module. It reads the first btrfs superblock located 64 KiB inside the partition and checks the little-endian magic value `_BHRfS_M`.

The local buffer union models only enough of `struct btrfs_super_block` to reach the magic: checksum, FSID, bytenr, flags, and magic. If the partition is too short to contain the 64 KiB offset plus one sector, or the read fails, probing returns `NULL`. On a magic match it returns a `PedGeometry` spanning the entire input geometry.

The module registers one `PedFileSystemType` named `btrfs`. It does not validate checksum, generation, device size, or backup superblocks, so it is a signature detector rather than a consistency checker.
