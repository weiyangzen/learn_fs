# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/romfs.c

## Scope

Implements ROMFS probing.

## Behavior

- Reads the ROMFS superblock and verifies a big-endian additive checksum over up to 512 bytes, capped by the filesystem full size.
- Exports nonempty volume name, filesystem size, filesystem block size, and block size.
- Uses static magic `-rom1fs-`.

## Dependencies And Risks

- Checksum length must be 32-bit aligned.
- Failure to read the checksum-covered buffer is treated as a failed validation.
