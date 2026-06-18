# sources/distributed-fs/ceph-client/include/linux/mtd/nftl.h

## Purpose

Defines kernel-side state and helper prototypes for the NAND Flash Translation Layer block translation driver.

## Important APIs, Types, and Functions

Important pieces are `struct NFTLrecord`, `NFTL_mount()`, `NFTL_formatblock()`, table dump helpers, and `nftl_read_oob()`/`nftl_write_oob()`.

Source-visible symbols include structs: `struct NFTLrecord`, `struct mtd_blktrans_dev mbd;`, `struct NFTLMediaHeader MediaHdr;`, `struct erase_info instr;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: `int NFTL_mount(struct NFTLrecord *s);`, `int NFTL_formatblock(struct NFTLrecord *s, int block);`; representative macros: `__MTD_NFTL_H__`, `NFTL_MAJOR`, `MAX_NFTLS`, `MAX_SECTORS_PER_UNIT`, `NFTL_PARTN_BITS`.

## Control Flow

NFTL mount scans media headers and builds erase-unit and replacement-chain tables; block operations translate logical sectors to physical NAND pages and use OOB metadata for status.

## State and Persistence Behavior

Runtime state includes an embedded `mtd_blktrans_dev`, media header, erase size, use count, geometry, virtual unit chains, replacement/free block tracking, last free block, and erase instruction. Persistent state is NFTL metadata stored in flash and OOB.

## Dependencies and Integration Points

It depends on MTD core, block translation, and the user NFTL media-format header.

Direct includes observed in the source are: `#include <linux/mtd/mtd.h>`, `#include <linux/mtd/blktrans.h>`, `#include <mtd/nftl-user.h>`.

## Risks and Edge Cases

Translation-table corruption, free-block exhaustion, and OOB incompatibility can expose stale or wrong logical data.

## Test Signals

Mount golden NFTL images, test replacement chains, bad/deleted/free block handling, OOB helpers, and recovery from malformed metadata.

Source read signal: 57 lines, 1734 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
