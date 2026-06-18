# sources/distributed-fs/ceph-client/include/linux/mtd/ftl.h

## Purpose

Defines the on-media erase unit header and block allocation bit encodings for the historical Flash Translation Layer format.

## Important APIs, Types, and Functions

The central type is `erase_unit_header_t`; macros decode erase-unit flags and Block Allocation Information words with `BLOCK_FREE()`, `BLOCK_DELETED()`, `BLOCK_TYPE()`, `BLOCK_ADDRESS()`, and block type constants.

Source-visible symbols include structs: none visible in this header; enums: none visible in this header; typedefs: `typedef struct erase_unit_header_t {`; prototypes: none visible in this header; representative macros: `_LINUX_FTL_H`, `HIDDEN_AREA`, `REVERSE_POLARITY`, `DOUBLE_BAI`, `BLOCK_FREE`, `BLOCK_DELETED`, `BLOCK_TYPE`, `BLOCK_ADDRESS`, `BLOCK_NUMBER`, `BLOCK_CONTROL`, `BLOCK_DATA`, `BLOCK_REPLACEMENT`, `BLOCK_BAD`.

## Control Flow

FTL mount/format code reads erase-unit headers from flash, interprets tuple fields and BAM offsets, then classifies block mappings using the macros in this header.

## State and Persistence Behavior

The header describes persistent flash metadata: erase counts, logical erase-unit numbers, formatted size, alternate header offset, BAM offset, flags, serial number, and block-state words.

## Dependencies and Integration Points

It relies on fixed-width integer types and is consumed by the FTL block translation implementation.

Direct includes observed in the source are: none visible in this header.

## Risks and Edge Cases

Endian/layout drift would corrupt format interpretation. The macros assume exact legacy bit encodings; accepting partially erased or power-failed BAM words needs defensive callers.

## Test Signals

Use golden FTL images with free, deleted, control, data, replacement, and bad block entries, plus malformed erase-unit headers.

Source read signal: 74 lines, 2551 bytes. The report is based on a complete pass over the header and symbol inventory for this work item.
