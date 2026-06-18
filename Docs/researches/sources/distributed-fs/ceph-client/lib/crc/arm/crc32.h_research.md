# sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc32.h` dispatches ARM CRC32/CRC32C calls between generic tables, ARMv8 CRC instructions, and PMULL acceleration.

## Important APIs, Types, and Functions

It defines static keys `have_crc32` and `have_pmull`, threshold `PMULL_MIN_LEN`, assembly declarations for CRC32 and CRC32C PMULL/scalar routines, inline functions `crc32_le_scalar`, `crc32_le_arch`, `crc32c_scalar`, `crc32c_arch`, `crc32_optimizations_arch`, and `crc32_mod_init_arch`.

## Control Flow

Scalar helpers use hardware CRC instructions if `have_crc32` is enabled, else generic base tables. Long little-endian CRC32/CRC32C calls align the buffer to 16 bytes using scalar processing, run PMULL on a rounded-down 16-byte multiple under `scoped_ksimd()`, then process tails through scalar helpers. Big-endian CRC32 falls back to generic.

## State and Persistence Behavior

Static keys are enabled after init based on `elf_hwcap2` bits. There is no per-call persistent state.

## Dependencies and Integration Points

The header depends on ARM hwcap, cpufeature, SIMD helpers, assembly routines in `arm/crc32-core.S`, and generic base functions from `crc32-main.c`.

## Risks and Edge Cases

Feature bits must match actual instruction availability. PMULL dispatch must honor `may_use_simd()` and avoid calling with too-short or unaligned chunks. The reported optimization flags must reflect only enabled runtime capabilities.

## Test Signals

Signals include no-feature generic fallback, CRC instruction-only systems, PMULL systems, unaligned input, length around `PMULL_MIN_LEN + 15`, `crc32_optimizations()` flags, and generic equality tests.

## Read Coverage

Source read size: 96 lines, 2503 bytes.
