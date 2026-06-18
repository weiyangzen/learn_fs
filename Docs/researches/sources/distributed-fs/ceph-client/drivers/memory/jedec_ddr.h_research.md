# sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr.h

## Purpose
`jedec_ddr.h` provides JEDEC DDR and LPDDR metadata shared by memory-controller drivers and device-tree parsing helpers. It defines density/type/width encodings, mode-register constants, timing structures, and exported JEDEC LPDDR2 table declarations.

## Important APIs, Types, And Functions
The header defines DDR density macros from 64Mb through 32Gb, memory type macros for DDR2/DDR3/LPDDR2/LPDDR3, IO width encodings, row/column/bank constants, refresh and tRFC constants, mode-register numbers, LPDDR2 MR4 temperature masks, manufacturer IDs, and LPDDR2 architecture types.

Important structures are `struct lpddr2_addressing`, `struct lpddr2_timings`, `struct lpddr2_min_tck`, `union lpddr2_basic_config4`, `struct lpddr2_info`, `struct lpddr3_timings`, and `struct lpddr3_min_tck`. It declares `lpddr2_jedec_addressing_table`, `lpddr2_jedec_timings`, `lpddr2_jedec_min_tck`, and `lpddr2_jedec_manufacturer()`.

## Control Flow
The header has no control flow. Consumers use the encoded constants to convert device-tree or mode-register values into controller-specific register settings.

## State And Persistence
It declares immutable JEDEC data tables implemented in `jedec_ddr_data.c`. Structures represent memory part properties and timing state but do not store global mutable state.

## Dependencies And Integration Points
It is used by `emif.c`, `of_memory.c`, and any DDR-capable memory controller needing LPDDR2/LPDDR3 timing descriptions. It depends only on `linux/types.h`.

## Risks
Consumers must consistently distinguish raw JEDEC encodings, device-tree human units, and controller encodings. Density/index conversion mistakes can select the wrong addressing-table row. LPDDR3 structures have no built-in default table in this header.

## Test Signals
Compile coverage plus consumers parsing LPDDR2 and LPDDR3 DT nodes are the main signals. Unit-style checks can validate density and IO-width conversions against expected table indexes and manufacturer names.
