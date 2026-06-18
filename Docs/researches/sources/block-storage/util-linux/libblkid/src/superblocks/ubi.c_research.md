# File Research: sources/block-storage/util-linux/libblkid/src/superblocks/ubi.c

## Scope

Detects UBI erase counter headers.

## Behavior

- Reads `UBI#` erase counter header.
- Verifies header CRC over all bytes before `hdr_crc`.
- Exports UBI version and formats `image_seq` as UUID.

## Dependencies And Risks

- Uses big-endian fields for CRC and image sequence.
- Classified as RAID usage in libblkid because UBI is a volume/container layer rather than a regular filesystem.
