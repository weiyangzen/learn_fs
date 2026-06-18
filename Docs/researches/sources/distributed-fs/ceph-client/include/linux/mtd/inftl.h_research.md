# sources/distributed-fs/ceph-client/include/linux/mtd/inftl.h

## Purpose

Defines kernel-side state and helper prototypes for the Inverse NAND Flash Translation Layer block translation driver.

## Important APIs, Types, and Functions

Important APIs are `INFTL_mount()`, `INFTL_formatblock()`, dump helpers, OOB read/write helpers, and `struct INFTLrecord` embedding `mtd_blktrans_dev`.

Source-visible symbols include structs: `struct INFTLrecord`, `struct mtd_blktrans_dev mbd;`, `struct INFTLMediaHeader MediaHdr;`, `struct erase_info instr;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int INFTL_mount(struct INFTLrecord *s);`, `int INFTL_formatblock(struct INFTLrecord *s, int block);`, `void INFTL_dumptables(struct INFTLrecord *s);`, `void INFTL_dumpVUchains(struct INFTLrecord *s);`; representative macros: `__MTD_INFTL_H__`, `INFTL_MAJOR`, `INFTL_PARTN_BITS`.

## Control Flow

Mount reads INFTL media headers and builds physical-unit and virtual-unit tables. Block formatting and OOB helpers operate through the underlying `mtd_info` while the block translation layer exposes disk geometry.

## State and Persistence Behavior

Runtime state includes media unit, erase size, media header, use count, CHS geometry, virtual/physical unit tables, free-unit tracking, boot-block counts, and a reusable `erase_info`. Persistent state is the INFTL media header and translation metadata stored on flash/OOB.

## Dependencies and Integration Points

It depends on MTD block translation, MTD core, NFTL definitions, and the user-visible INFTL header.

Direct includes observed in the source are: `#include <linux/mtd/blktrans.h>`, `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/nftl.h>`, `#include <mtd/inftl-user.h>`.

## Risks and Edge Cases

PU/VU table corruption or mismatched OOB semantics can remap logical blocks incorrectly. Geometry fields are legacy but still affect block device behavior.

## Test Signals

Mount known INFTL images, format blocks, verify PU/VU chains, exercise OOB helpers across page boundaries, and test malformed media headers.

Source read signal: 63 lines, 1599 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
