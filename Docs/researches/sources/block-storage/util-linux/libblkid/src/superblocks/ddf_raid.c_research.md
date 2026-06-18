# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ddf_raid.c

SNIA DDF RAID member detector. It checks possible secondary header locations near the end of the disk, validates the big-endian DDF signature and CRC32 with the CRC field excluded and treated as `0xff`, and optionally confirms the primary header by reading the recorded primary LBA.

On match it stores the 24-byte DDF GUID as UUID, copies the revision string into `VERSION`, and records the magic offset for wiping/reporting. It reports `ddf_raid_member` with RAID usage and a minimum size. Detection is size-position based rather than static magic-table based.
