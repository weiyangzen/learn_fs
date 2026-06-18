# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/adaptec_raid.c

Adaptec RAID member detector. It checks only regular files or whole-disk block devices, reads vendor metadata from the last 512-byte sector, and validates two big-endian markers: the `DPTM` signature and the Adaptec magic value.

On match, it reports `adaptec_raid_member`, usage `BLKID_USAGE_RAID`, stores the metadata revision as `VERSION`, and records the signature location through `blkid_probe_set_magic` when magic reporting is enabled. It has no magic table because the probe location is computed from device size. False-positive resistance is based on whole-disk restriction plus dual magic validation.
