<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h

## Purpose
Defines the legacy NFTL on-flash metadata layout for NAND Flash Translation Layer media, including OOB records, media headers, erase-zone constants, sector states, and fold markers.

## Important APIs, Types, and Functions
Read coverage: 91 lines and 2116 bytes. Visible type families include struct nftl_bci, struct nftl_uci0, struct nftl_uci1, struct nftl_uci2, union nftl_uci, struct nftl_oob, struct NFTLMediaHeader. Important macros/constants include __MTD_NFTL_USER_H__, MAX_ERASE_ZONES, ERASE_MARK, SECTOR_FREE, SECTOR_USED, SECTOR_IGNORE, SECTOR_DELETED, FOLD_MARK_IN_PROGRESS, ZONE_GOOD, ZONE_BAD_ORIGINAL, ZONE_BAD_MARKED. Explicit ioctl-style command names include none.

## Control Flow
There are no functions. Userspace and kernel compatibility paths read OOB metadata, decode unit control information, inspect the media header, and use sector state constants to interpret free, used, ignored, and deleted sectors.

## State and Persistence Behavior
Persistent state is the NFTL media format itself: virtual unit numbers, erase marks, sector replacement information, erase-zone bookkeeping, bad-zone classification, and fold-in-progress markers stored on flash.

## Dependencies and Integration Points
It depends on Linux integer aliases and legacy NAND/NFTL conventions. It integrates with historical NFTL drivers and flash-maintenance tools that must understand old M-Systems formats. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
NFTL state is on-media and often encountered during recovery, so parsers must tolerate corrupt OOB/header data. Structure layout and magic constants are compatibility-sensitive and endian-sensitive.

## Test Signals
Check structure sizes and constants against known NFTL images, parse good and intentionally damaged media, validate big-endian behavior, and compile old NFTL tools against the exported header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/nftl-user.h -->
