# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/zfs.c

## Scope

Implements ZFS vdev label detection and nvlist metadata extraction.

## Behavior

- Computes the four ZFS label locations, skipping whole-disk label areas covered by partitions.
- Reads the nvpair area, validates XDR encoding, endian marker, and nonzero first nvpair size.
- Parses nested nvlists with bounds checks, first finding a plausible label by `guid`, `state`, and `txg`.
- Extracts pool label (`name`), device GUID as `UUID_SUB`, pool GUID as `UUID`, `ashift` block size, and version.
- Records the nvlist header as magic and exports native/other endianness.

## Dependencies And Risks

- Uses unaligned-safe big-endian reads for nvlist fields.
- Parser bounds checks name/value sizes and directory nesting, but only supports the needed scalar/string/directory types.
- Minimum device size is 64 MiB; labels on partition-covered areas are skipped for whole-disk probing.
