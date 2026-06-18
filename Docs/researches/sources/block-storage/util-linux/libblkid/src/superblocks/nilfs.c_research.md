# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/nilfs.c

## Scope

Implements NILFS2 filesystem probing for libblkid.

## Behavior

- Defines the packed NILFS superblock layout and primary/backup offsets.
- `nilfs_valid_sb()` validates magic, backup device size on whole-disk probes, superblock byte length, and CRC over the checksum-excluded region.
- `probe_nilfs2()` reads the primary superblock at `0x400` and backup near the end of the device, tolerating backup read errors when the primary is valid.
- Selects the newer valid superblock by checkpoint number, then exports label, UUID, revision, magic location, filesystem block size, and block size.

## Dependencies And Risks

- Uses `blkid_probe_get_buffer()`, checksum verification, endian helpers, and result setters from the superblock framework.
- Block-size shifts above 6 are ignored to avoid overflow and to match kernel NILFS limits.
- Backup probing depends on `pr->size`; invalid or tiny media can make only the primary usable.
