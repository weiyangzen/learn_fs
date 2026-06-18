# sources/distributed-fs/ceph-client/include/linux/mtd/sharpsl.h

## Purpose

Defines SharpSL NAND platform data for legacy Sharp handheld boards.

## Important APIs, Types, and Functions

The exported type is `struct sharpsl_nand_platform_data` with bad-block pattern, ECC OOB layout, partitions, partition count, and parser names.

Source-visible symbols include structs: `struct sharpsl_nand_platform_data`, `struct nand_bbt_descr	*badblock_pattern;`, `struct mtd_partition	*partitions;`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `_MTD_SHARPSL_H`.

## Control Flow

The SharpSL NAND driver uses this board data to choose BBT scanning, ECC layout, and partition registration for its raw NAND chip.

## State and Persistence Behavior

Only static platform metadata is described.

## Dependencies and Integration Points

It depends on raw NAND and partition APIs.

Direct includes observed in the source are: `#include <linux/mtd/rawnand.h>`, `#include <linux/mtd/partitions.h>`.

## Risks and Edge Cases

Wrong bad-block pattern or ECC layout can make existing media unreadable or mark blocks incorrectly.

## Test Signals

Board probe, bad-block-pattern scans, ECC-layout compatibility, and fixed/parser partition registration.

Source read signal: 22 lines, 485 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
