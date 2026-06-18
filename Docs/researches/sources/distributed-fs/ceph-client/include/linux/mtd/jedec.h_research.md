# sources/distributed-fs/ceph-client/include/linux/mtd/jedec.h

## Purpose

Models the JEDEC NAND parameter page layout and related feature/optional-command bits.

## Important APIs, Types, and Functions

Key types are packed `struct jedec_ecc_info` and `struct nand_jedec_params`, plus feature macros such as `JEDEC_FEATURE_16_BIT_BUS` and `JEDEC_OPT_CMD_READ_CACHE`.

Source-visible symbols include structs: `struct jedec_ecc_info`, `struct nand_jedec_params`, `struct jedec_ecc_info ecc_info[4];`; enums: none visible in this header; typedefs: none visible in this header; prototypes: none visible in this header; representative macros: `__LINUX_MTD_JEDEC_H`, `JEDEC_FEATURE_16_BIT_BUS`, `JEDEC_OPT_CMD_READ_CACHE`.

## Control Flow

Raw NAND identification code reads parameter pages, validates the signature and CRC elsewhere, then copies fields from this packed layout into NAND memory organization and ECC requirement structures.

## State and Persistence Behavior

This is a persistent wire/on-flash description format: manufacturer/model, JEDEC ID, page/OOB/block/LUN geometry, timing grades, optional commands, ECC/endurance data, vendor revision, and CRC.

## Dependencies and Integration Points

It depends on fixed-width and little-endian Linux types and is included by raw NAND identification code.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Packed layout and little-endian fields must exactly match the standard. Callers must validate CRC and parameter-page count before trusting geometry.

## Test Signals

Parse golden JEDEC parameter pages, reject bad signatures/CRC, and verify ECC/endurance fields map into `nand_ecc_props` correctly.

Source read signal: 94 lines, 1973 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
