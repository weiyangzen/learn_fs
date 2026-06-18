# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/via_raid.c

## Scope

Detects VIA RAID member metadata.

## Behavior

- Reads metadata from the final sector of whole disks or regular files.
- Validates signature `0xAA55`, version <= 2, and 8-bit checksum over the first 50 bytes.
- Exports version and records the signature as magic.

## Dependencies And Risks

- No probing of partitions is allowed.
- The checksum includes the stored checksum byte behavior as defined by VIA metadata expectations.
