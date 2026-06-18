# sources/distributed-fs/ceph-client/drivers/memory/jedec_ddr_data.c

## Purpose
`jedec_ddr_data.c` implements exported LPDDR2 JEDEC addressing, timing, minimum-cycle, and manufacturer-name data used as defaults or reference data by memory-controller drivers.

## Important APIs, Types, And Functions
It defines and exports `lpddr2_jedec_addressing_table`, `lpddr2_jedec_timings`, `lpddr2_jedec_min_tck`, and `lpddr2_jedec_manufacturer()`. The addressing table maps density classes to bank count, refresh interval, and all-bank refresh timing. The timing table covers LPDDR2 speed bins 400, 533, 800, and 1066. The minimum-tCK structure supplies cycle minima for timings such as tRPab, tRCD, tWR, tRRD, tWTR, and tFAW.

## Control Flow
There is no dynamic control flow except `lpddr2_jedec_manufacturer()`, which switches on manufacturer ID constants and returns a static string, defaulting to `"invalid"`.

## State And Persistence
All data is immutable `const` global state exported to other GPL kernel code. There is no runtime allocation or persistence.

## Dependencies And Integration Points
The file includes `jedec_ddr.h` and `linux/export.h`. `emif.c` uses the tables for default timings and addressing calculations; `of_memory.c` falls back to `lpddr2_jedec_min_tck` and `lpddr2_jedec_timings` when DT data is incomplete.

## Risks
The addressing array declares `NUM_DDR_ADDR_TABLE_ENTRIES` as 11 while this initializer provides 10 entries, leaving a zero-filled row if indexed. Consumers must avoid unsupported density/type combinations. Timing values are JEDEC defaults and may not match board-specific margins.

## Test Signals
Tests should confirm exported symbols link, default timing fallback produces four frequency entries, manufacturer IDs return expected names, and each supported EMIF density/type conversion lands on an initialized addressing entry.
