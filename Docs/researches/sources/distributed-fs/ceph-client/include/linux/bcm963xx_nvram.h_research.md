# sources/distributed-fs/ceph-client/include/linux/bcm963xx_nvram.h

## Purpose
Defines the Broadcom BCM963xx board NVRAM layout, size/version constants, NAND partition helpers, and an inline checksum verifier.

## Important APIs, types, and functions
- `BCM963XX_NVRAM_V4_SIZE`, `BCM963XX_NVRAM_V5_SIZE`, and `BCM963XX_DEFAULT_PSI_SIZE` define versioned layout sizes.
- `enum bcm963xx_nvram_nand_part` indexes boot, rootfs, data, and BBT partition arrays.
- `struct bcm963xx_nvram` lays out bootline, board name, PSI size, MAC count/base, v4 checksum, NAND offsets/sizes, and v5 checksum.
- `bcm963xx_nvram_nand_part_offset()` and `_size()` convert KiB fields to bytes.
- `bcm963xx_nvram_checksum()` verifies CRC32 with the checksum field treated as zero.

## Control flow and state
Boot/platform code reads the persistent NVRAM block, verifies checksum according to `version`, then consumes fixed fields and NAND partition descriptors. Macros provide named partition access.

## State and persistence behavior
The structure maps persistent firmware NVRAM. Offsets and sizes are stored in KiB and converted to bytes. Checksum choice depends on layout version: v4 uses the 300-byte minimum, newer versions use 1 KiB.

## Dependencies and integration points
Depends on CRC32, Ethernet address length, size macros, and fixed-width types. Integrated by BCM63xx/BCM963xx platform boot, MTD partitioning, and network MAC provisioning.

## Risks
Do not use `sizeof(struct bcm963xx_nvram)` to decide firmware data length; comments require versioned minimum sizes. Endianness and untrusted flash contents must be handled by callers. Bad checksum should prevent trusting partition/MAC data.

## Test signals
Use known-good v4/v5 NVRAM images, checksum mismatch images, boundary partition indexes, KiB-to-byte conversion checks, and corrupted version values.
