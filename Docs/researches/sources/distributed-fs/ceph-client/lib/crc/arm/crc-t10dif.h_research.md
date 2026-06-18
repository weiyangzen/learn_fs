# sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h

## Purpose

`sources/distributed-fs/ceph-client/lib/crc/arm/crc-t10dif.h` is the ARM dispatch header included by `crc-t10dif-main.c` when architecture optimization is enabled. It selects NEON or PMULL implementations based on runtime CPU features and SIMD availability.

## Important APIs, Types, and Functions

It defines static keys `have_neon` and `have_pmull`, chunk threshold `CRC_T10DIF_PMULL_CHUNK_SIZE`, assembly declarations `crc_t10dif_pmull64` and `crc_t10dif_pmull8`, inline `crc_t10dif_arch`, and `crc_t10dif_mod_init_arch`.

## Control Flow

`crc_t10dif_arch()` checks that the length is at least 16 and `may_use_simd()` is true. If PMULL is available, it enters `scoped_ksimd()` and returns `crc_t10dif_pmull64()`. If only NEON is available and length is greater than 16, it folds into a 16-byte buffer with `crc_t10dif_pmull8()` under SIMD context, then finishes using `crc_t10dif_generic(0, buf, 16)`. Otherwise it falls back to generic.

## State and Persistence Behavior

Runtime feature state is held in read-only-after-init static keys enabled during module/subsys init from `elf_hwcap` and `elf_hwcap2`. No per-call persistent state exists.

## Dependencies and Integration Points

The header depends on ARM SIMD context helpers, hardware capability bits `HWCAP_NEON` and `HWCAP2_PMULL`, and generic T10DIF code in `crc-t10dif-main.c`.

## Risks and Edge Cases

The dispatch must never call assembly when SIMD is unavailable. The NEON-only fallback deliberately uses generic reduction for the final vector; changing that contract can break CRC output. Static key initialization must happen before performance-sensitive use but fallback remains correct before init.

## Test Signals

Signals include feature-detection tests for no NEON, NEON-only, and PMULL systems, preemption/SIMD context assertions, generic equivalence over length thresholds, and module init enabling static keys.

## Read Coverage

Source read size: 46 lines, 1348 bytes.
