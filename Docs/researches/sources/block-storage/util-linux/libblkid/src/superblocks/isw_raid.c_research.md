# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/isw_raid.c

Intel Matrix Storage RAID member detector. It applies only to regular files or whole disks, reads metadata two logical sectors from the end using the probed sector size, and checks the `Intel Raid ISM Cfg Sig. ` prefix.

On match it formats the version from the signature suffix and records the signature as magic. It reports `isw_raid_member` with RAID usage and a 64 KiB minimum size. No checksum validation is performed in this detector.
