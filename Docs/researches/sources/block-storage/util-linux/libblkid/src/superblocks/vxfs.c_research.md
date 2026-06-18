# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/vxfs.c

## Scope

Implements Veritas VxFS probing.

## Behavior

- Supports little-endian and big-endian magics at different offsets.
- Uses the magic hint to convert version and block size.
- Exports version, filesystem block size, block size, and endianness.

## Dependencies And Risks

- Correctness depends on the idinfo hint matching the magic byte order.
- No label or UUID extraction is implemented.
