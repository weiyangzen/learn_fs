# File Research: sources/block-storage/mdadm/crc32.h

## Purpose
`crc32.h` is a generated lookup-table header for fast CRC-32 calculation.

## Contents
It defines `crc_table[TBLS][256]` as `local const unsigned long FAR`, with the base 256-entry CRC table and conditional additional tables for `BYFOUR`.

## Integration Notes
The header is included directly by `crc32.c` when dynamic CRC table generation is disabled. It depends on `local`, `FAR`, and `TBLS` being defined by the including source.

## Risks
This is generated data; hand edits risk corrupting CRC results. The conditional `BYFOUR` sections must stay in sync with `crc32.c` table-generation logic.
