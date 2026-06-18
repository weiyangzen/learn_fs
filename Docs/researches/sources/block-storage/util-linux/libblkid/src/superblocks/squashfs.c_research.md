# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/squashfs.c

## Scope

Implements SquashFS v4+ and SquashFS v3 probing.

## Behavior

- SquashFS v4+ uses little-endian `hsqs`, rejects versions below 4, and exports version, block size, and bytes used as filesystem size.
- SquashFS3 handles both big-endian `sqsh` and little-endian `hsqs`, rejects versions above 3, and exports version, 1024-byte block size, and endianness.
- Registers separate idinfos: `squashfs` and `squashfs3`.

## Dependencies And Risks

- Version split is necessary because `hsqs` can identify both old and new little-endian formats.
- The v3 path does not export filesystem size from this shared structure.
