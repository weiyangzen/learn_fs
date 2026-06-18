# sources/distributed-fs/ceph-client/lib/zstd/compress/zstd_ldm_geartab.h

## Purpose

`zstd_ldm_geartab.h` provides the fixed 256-entry gear hash table used by long distance matching. Each byte value maps to a 64-bit pseudo-random constant. `zstd_ldm.c` combines these constants with a left-shift rolling hash to find content-defined split points.

## Important APIs, Types, and Functions

The header exports one internal object: `static UNUSED_ATTR const U64 ZSTD_ldm_gearTab[256]`. It includes `compiler.h` for `UNUSED_ATTR` and `mem.h` for `U64`. There are no functions and no public runtime API.

## Control Flow

This file contributes data to the control flow in `ZSTD_ldm_gear_reset()` and `ZSTD_ldm_gear_feed()`. For each input byte, those functions update `hash = (hash << 1) + ZSTD_ldm_gearTab[inputByte]`. A stop mask derived from `hashRateLog` and `minMatchLength` determines when a rolling hash value is accepted as a split point.

## State and Persistence Behavior

The table is immutable and file-local because it is declared `static const`. Every translation unit that includes this header gets its own internal copy unless the compiler/linker folds constants. It does not persist dynamic state, but changing any constant changes LDM split-point distribution and therefore compression behavior.

## Dependencies and Integration Points

The only observed consumer in this subset is `zstd_ldm.c`. The table is part of the LDM algorithm contract: `ZSTD_ldm_gear_init()` chooses high-weight mask bits based on assumptions about how gear hash bits depend on recent bytes. The `UNUSED_ATTR` annotation allows the header to be included in configurations where LDM helpers are compiled out or optimized away.

## Risks

The constants must remain deterministic across builds and platforms. Any accidental edit can alter compression ratio, speed, and reproducibility. Because the table is a header-local `static` object, including it broadly can add object size. Endianness is not a direct risk for the table values because indexing is byte-based, but `U64` width and literal parsing must remain stable.

## Test Signals

Useful tests are mostly indirect: LDM split-rate tests for selected `hashRateLog` values, round-trip compression with LDM enabled, and reproducibility checks that the same input and parameters produce the same sequence decisions. Static checks can verify the table has exactly 256 entries and compiles in kernel mode.
