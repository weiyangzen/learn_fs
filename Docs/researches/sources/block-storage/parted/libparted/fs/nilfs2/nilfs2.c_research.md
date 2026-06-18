# File Research: sources/block-storage/parted/libparted/fs/nilfs2/nilfs2.c

NILFS2 filesystem probe module with CRC validation. It defines the packed NILFS2 superblock layout, primary superblock offset, and macro for computing the secondary superblock offset from device size in 512-byte units.

`is_valid_nilfs_sb()` checks little-endian magic `0x3434`, validates the superblock byte count, and recomputes the EFI CRC32 over the superblock with the checksum field treated as zero. `nilfs2_probe()` converts the candidate geometry length to 512-byte units, computes the secondary superblock offset, reads the primary superblock from byte offset 1024, validates it, reads the secondary superblock near the end, validates it, then returns a geometry ending after the reserved 4 KiB secondary-superblock area.

The module registers one filesystem type named `nilfs2`. It is stricter than many other probes because both primary and secondary superblocks must pass checksum validation.
