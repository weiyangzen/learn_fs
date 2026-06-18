# sources/distributed-fs/ceph-client/drivers/memory/of_memory.c

## Purpose
`of_memory.c` provides exported OpenFirmware/device-tree helpers for DDR memory descriptions. It parses LPDDR2 and LPDDR3 timing, minimum-cycle, and chip identity properties into JEDEC structures for memory-controller drivers.

## Important APIs, Types, And Functions
Exported APIs are `of_get_min_tck()`, `of_get_ddr_timings()`, `of_lpddr3_get_min_tck()`, `of_lpddr3_get_ddr_timings()`, and `of_lpddr2_get_info()`. Internal helpers `of_do_get_timings()` and `of_lpddr3_do_get_timings()` parse one timing child node.

LPDDR2 helpers allocate devm structures, read required properties, and fall back to `lpddr2_jedec_min_tck` or `lpddr2_jedec_timings` when allocation or parsing fails. LPDDR3 helpers return NULL on failure rather than a JEDEC default table. `of_lpddr2_get_info()` parses revision IDs, IO width, density, architecture type from compatible strings, and manufacturer from compatible vendor prefixes.

## Control Flow
Timing collection counts compatible child nodes first, allocates an array, then loops again to populate entries. Any missing required property frees the allocation and goes to fallback. LPDDR2 info parsing first handles the newer `revision-id` array with fallback to `revision-id1`/`revision-id2`, then validates mandatory `io-width` and `density`, determines architecture type, scans compatible strings for known vendors, and returns a devm-allocated copy.

## State And Persistence
All returned dynamic structures are devm-managed against the requesting device. Fallback LPDDR2 data points to global const JEDEC tables. The helpers do not persist state across calls.

## Dependencies And Integration Points
The file depends on OF property helpers, `jedec_ddr.h`, `of_memory.h`, devm allocation, and exported symbols. `emif.c` uses these APIs to build platform data from memory device nodes.

## Risks
The helpers require complete timing child nodes; one missing property discards all custom timings. LPDDR2 density and IO-width conversions assume power-of-two values and specific DT units. LPDDR3 has no default fallback, so callers must handle NULL. Vendor detection depends on compatible strings formatted as `vendor,...`.

## Test Signals
Tests should parse complete and incomplete LPDDR2/LPDDR3 nodes, verify fallback warnings and frequency counts, validate deprecated LPDDR3 `reg` max-frequency fallback, and confirm `of_lpddr2_get_info()` encodes manufacturer, density, IO width, and revisions as expected.
