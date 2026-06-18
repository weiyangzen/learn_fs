# File Research: sources/block-storage/lvm2/lib/misc/crc.h

This header declares the CRC helper.

Content:
- Defines `INITIAL_CRC` as `0xf597a6cf`.
- Declares `uint32_t calc_crc(uint32_t initial, const uint8_t *buf, size_t size)`.

Dependencies:
- Includes `<inttypes.h>`.

Role:
- Shared metadata/checksum users include this header for LVM’s CRC-32 implementation.
