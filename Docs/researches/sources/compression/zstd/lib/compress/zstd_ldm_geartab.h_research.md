# sources/compression/zstd/lib/compress/zstd_ldm_geartab.h

## Purpose
`zstd_ldm_geartab.h` provides the 256-entry 64-bit gear table used by LDM's rolling hash to create content-defined split points.

## Important APIs, Types, And Functions
The file defines one internal object, `static UNUSED_ATTR const U64 ZSTD_ldm_gearTab[256]`. Each byte value indexes a precomputed 64-bit constant used in `hash = (hash << 1) + table[input_byte]`.

## Control Flow
There is no control flow. `zstd_ldm.c` includes the table and reads it from the gear hash reset/feed loops.

## State And Persistence
The table is immutable static data. It creates no runtime state and writes no persistent data.

## Dependencies And Integration Points
It includes common compiler and memory headers for `UNUSED_ATTR` and `U64`. Its only direct consumer in this subset is `ZSTD_ldm_gear_reset()` and `ZSTD_ldm_gear_feed()` in `zstd_ldm.c`.

## Risks
Changing table values changes split-point distribution, which can significantly alter LDM compression ratio and speed. Because it is a header-defined `static` table, inclusion in many translation units would duplicate data, though current usage is narrow and `UNUSED_ATTR` suppresses unused warnings.

## Test Signals
There are no direct unit tests. Strong indirect signals are stable LDM ratio/speed benchmarks, deterministic compression output for fixed parameters, and fuzz/round-trip coverage of large inputs with LDM enabled.
