# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/jmicron_raid.c

JMicron RAID member detector. It checks regular-file/whole-disk scope, reads metadata from the last sector, validates the `JM` signature, verifies a 16-bit additive checksum whose sum must be 0 or 1, and rejects RAID mode values above 5.

On success it reports version as major.minor from the packed version field and records the signature magic offset. It reports `jmicron_raid_member` with RAID usage and a 64 KiB minimum size.
