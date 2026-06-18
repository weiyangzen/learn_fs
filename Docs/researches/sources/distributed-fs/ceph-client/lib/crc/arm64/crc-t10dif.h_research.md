# sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm64/crc-t10dif.h` dispatches CRC-T10DIF on arm64 between generic, ASIMD p8 folding, and PMULL p64 acceleration.

## Important APIs, Types, and Functions

It defines static keys `have_asimd` and `have_pmull`, `CRC_T10DIF_PMULL_CHUNK_SIZE`, assembly declarations `crc_t10dif_pmull_p8` and `crc_t10dif_pmull_p64`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

For lengths at least 16 and allowed SIMD context, PMULL-enabled CPUs call `crc_t10dif_pmull_p64()`. ASIMD-only CPUs with length greater than 16 call `crc_t10dif_pmull_p8()` into a stack buffer and finish with generic CRC over that folded buffer. Other cases use `crc_t10dif_generic()`.

## State and Persistence Behavior

Feature state is stored in read-only-after-init static keys enabled from `cpu_have_named_feature(ASIMD)` and `cpu_have_named_feature(PMULL)`.

## Dependencies and Integration Points

The header depends on arm64 cpufeature and SIMD helpers, the assembly implementation, and the generic T10DIF main file.

## Risks and Edge Cases

Dispatch must respect `may_use_simd()` and length constraints. The ASIMD-only path's stack buffer must be valid for generic finishing. Static key setup must match CPU feature alternatives.

## Test Signals

Signals include generic/ASIMD/PMULL path equivalence, length thresholds 15/16/17, runtime feature flags, SIMD-disabled context fallback, and KUnit coverage with benchmarks for acceleration paths.

## Read Coverage

Source read size: 48 lines, 1398 bytes.
