<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h -->
# sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h

## Purpose
Defines the historical INFTL on-flash layout structures used by userspace tooling and kernel code to inspect or format M-Systems-style flash translation layer media.

## Important APIs, Types, and Functions
Read coverage: 92 lines and 1644 bytes. Visible type families include struct inftl_bci, struct inftl_unithead1, struct inftl_unithead2, struct inftl_unittail, union inftl_uci, struct inftl_oob, struct INFTLPartition, struct INFTLMediaHeader. Important macros/constants include __MTD_INFTL_USER_H__, OSAK_VERSION, PERCENTUSED, SECTORSIZE, INFTL_BINARY, INFTL_BDTL, INFTL_LAST. Explicit ioctl-style command names include none.

## Control Flow
There are no callable routines. Tools read OOB bytes into `struct inftl_oob`, interpret the unit-control union, and parse `INFTLMediaHeader` partitions and erase-unit metadata to discover virtual-unit chains and formatted size.

## State and Persistence Behavior
The structures describe persistent media state stored in NAND OOB and header erase units: block control information, erase mark values, virtual unit numbers, previous/next chains, free/deleted sectors, partition records, and boot-record identifiers.

## Dependencies and Integration Points
It uses Linux fixed-width integer aliases and little-endian on-media fields. It integrates with legacy INFTL/NAND tooling and any compatibility code that still parses INFTL volumes. Direct includes are #include <linux/types.h>.

## Risks and Edge Cases
This is an on-flash ABI; packing, field width, array size, and endian assumptions must not change. Corrupt headers or OOB values can create invalid erase-unit chains, and modern MTD code must avoid treating these legacy structures as native-endian kernel-only data.

## Test Signals
Validate structure sizes against known INFTL images, parse representative good and corrupt media headers, check endian conversion on big-endian builds, and run old userspace format/inspect tools against the exported header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/mtd/inftl-user.h -->
