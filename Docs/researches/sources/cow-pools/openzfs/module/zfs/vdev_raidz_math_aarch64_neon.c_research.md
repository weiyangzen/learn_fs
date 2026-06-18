# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon.c

## Scope

This file registers the baseline AArch64 NEON RAID-Z math implementation and provides the shared precomputed GF(2^8) multiplication lookup table used by SIMD parity/reconstruction paths. It is part of subset A through `sources/cow-pools/openzfs`.

The source was read completely, lines 1-2280.

## Primary Interfaces

- `DEFINE_GEN_METHODS(aarch64_neon)` instantiates RAID-Z parity generation methods from `vdev_raidz_math_impl.h`.
- `DEFINE_REC_METHODS(aarch64_neon)` instantiates reconstruction methods from the same template.
- `raidz_will_aarch64_neon_work()` gates use on `kfpu_allowed()`.
- `vdev_raidz_aarch64_neon_impl` publishes the implementation as `"aarch64_neon"`.
- `gf_clmul_mod_lt[4*256][16]` is an aligned global lookup table consumed by the AArch64 common header and x86 AVX2/AVX512BW code.

## Architecture Configuration

The implementation is compiled only under `defined(__aarch64__)`. It includes `vdev_raidz_math_aarch64_neon_common.h`, then sets stride/register macros before including `vdev_raidz_math_impl.h`.

All regular zero/copy/add/multiply/generate/syndrome loops use 4 vector registers per step. Two-target and three-target recovery cases mostly use 2-register recovery strides, matching the common NEON helper's supported register counts and limiting temporary register pressure.

The macro groups define which NEON vector variables are live for each generated routine:
- `ZERO_*`, `COPY_*`, `ADD_*`, and `MUL_*` configure generic ABD buffer helpers.
- `GEN_P*` configure P, PQ, and PQR parity generation.
- `SYN_*` configure syndrome generation for Q, R, PQ, PR, QR, and PQR recovery.
- `REC_*` configure final recovery transforms for two- and three-column reconstruction.

## Lookup Table

After the implementation registration block, the file defines `gf_clmul_mod_lt` as a 256-byte-aligned table with `4 * 256` rows of 16 bytes. Each coefficient has four 16-byte subtables. The NEON common header's `MUL(c, ...)` macro indexes these rows to multiply vector bytes by arbitrary GF constants using nibble extraction and table lookup.

The same symbol is declared `extern` by `vdev_raidz_math_aarch64_neon_common.h`, `vdev_raidz_math_avx2.c`, and `vdev_raidz_math_avx512bw.c`, so this file is also the table provider for those lookup/shuffle implementations when linked into the OpenZFS RAID-Z math module set.

## Dependencies

- `sys/isa_defs.h` and `sys/types.h` provide platform and fixed-width type definitions.
- `vdev_raidz_math_aarch64_neon_common.h` supplies NEON vector primitives.
- `sys/vdev_raidz_impl.h` supplies RAID-Z row, column, target, and method-table contracts.
- `vdev_raidz_math_impl.h` supplies the shared algorithm template expanded under this architecture's macros.

## Filesystem Relevance

This is a CPU-specialized backend for the parity math used by ZFS RAID-Z vdevs. It accelerates P/Q/R parity generation and failed-column reconstruction on AArch64 systems with usable kernel FPU/SIMD context, while preserving the same high-level RAID-Z equations as the scalar/common implementations.

## Correctness Notes

- The implementation is not selected unless `kfpu_allowed()` is true.
- The table layout and alignment are part of the ABI expected by multiple architecture files; changing it would affect AArch64 NEON, AVX2, and AVX512BW multiplication.
- The generated routines rely on `vdev_raidz_math_impl.h` processing sizes in vector-aligned RAID-Z iteration units; this file only chooses strides and registers.
