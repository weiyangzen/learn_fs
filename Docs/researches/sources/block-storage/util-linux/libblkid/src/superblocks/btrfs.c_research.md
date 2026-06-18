# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/btrfs.c

Btrfs superblock detector, including zoned-device handling. For ordinary devices it reads the standard superblock at 64 KiB; for zoned devices it locates the active superblock log position by querying zone reports and interpreting conventional, empty, in-use, and full log-zone states.

Checksum validation supports CRC32C, XXH64, and SHA256 over the superblock payload, while unknown checksum types are logged and tolerated. On success it emits label, filesystem UUID, per-device UUID as `UUID_SUB`, sector/block size, total logical filesystem size, and last block.

False-positive defenses include checksum verification, nonzero sector size validation, magic offsets for both normal and zoned layouts, and careful zone-state validation. FSSIZE is explicitly logical and does not account for Btrfs RAID redundancy because that requires tree parsing.
