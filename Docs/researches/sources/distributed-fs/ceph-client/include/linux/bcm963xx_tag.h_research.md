# sources/distributed-fs/ceph-client/include/linux/bcm963xx_tag.h

## Purpose
Defines the Broadcom BCM963xx firmware image tag layout and constants used to parse or generate bootloader-compatible firmware headers.

## Important APIs, types, and functions
- Fixed field length macros describe tag version, signatures, board/chip IDs, image lengths, addresses, sequence, RSA placeholder, vendor info, and CRC fields.
- `BCM963XX_EXTENDED_SIZE` accounts for extended flash addressing that must be subtracted from tag offsets.
- `PIRELLI_BOARDS` names boards with alternate vendor info sizing.
- `struct bcm_tag` is a 256-byte header containing ASCII numeric fields plus several CRC32 fields.

## Control flow and state
Firmware tools or MTD parsers read the tag, validate board/chip identity and CRC fields, then derive kernel/rootfs/CFE locations and lengths. The comments describe the Broadcom bootloader assumption that rootfs starts the image and how OpenWrt-style kernel-first images encode addresses and lengths.

## State and persistence behavior
The tag is persistent on flash and controls bootloader flashing/validation behavior. Most numeric fields are character arrays, so parsing is string-based outside this header.

## Dependencies and integration points
Depends only on kernel types. Integrated by BCM963xx image parsers, MTD splitters, firmware builders, and board-specific update logic.

## Risks
Incorrect lengths or address interpretation can brick firmware upgrades. CRC fields cover different regions and must be computed exactly. Vendor variants such as Pirelli alter interpretation of information fields.

## Test signals
Parse representative firmware tags, validate CRC coverage, test kernel-first/rootfs-first images, extended flash address adjustment, board ID matching, and malformed ASCII length fields.
