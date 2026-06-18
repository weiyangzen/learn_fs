# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/lsi_raid.c

LSI MegaRAID member detector. It checks only regular files or whole disks, reads the last sector, and matches the six-byte `$XIDE$` signature.

On match it records the signature location through `blkid_probe_set_magic` and reports `lsi_mega_raid_member` with RAID usage and a 64 KiB minimum size. It does not expose UUID, label, version, or checksum validation.
