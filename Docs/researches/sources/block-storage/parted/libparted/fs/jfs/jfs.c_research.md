# File Research: sources/block-storage/parted/libparted/fs/jfs/jfs.c

Minimal JFS probe module. It reads the JFS aggregate superblock at byte offset 32768, verifies magic `"JFS1"`, and returns a geometry sized from the superblock’s physical block size and aggregate size.

The probe first checks that the candidate geometry is large enough to reach the superblock offset. It reads one device sector at `JFS_SUPER_OFFSET / sector_size` into the JFS superblock structure. On a match, it converts `s_pbsize` and `s_size` from little endian and computes length as `block_size * block_count / device_sector_size`.

The file registers a single filesystem type named `jfs`. It does not validate the superblock version, state, log fields, or secondary metadata.
