# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neonx2.c

## Scope

This file registers a more aggressively unrolled AArch64 NEON RAID-Z math implementation named `aarch64_neonx2`. It reuses the common AArch64 NEON primitive header and shared RAID-Z algorithm template, but chooses wider strides for several helper operations.

The source was read completely, lines 1-237.

## Primary Interfaces

- `DEFINE_GEN_METHODS(aarch64_neonx2)` instantiates generation methods.
- `DEFINE_REC_METHODS(aarch64_neonx2)` instantiates reconstruction methods.
- `raidz_will_aarch64_neonx2_work()` gates use on `kfpu_allowed()`.
- `vdev_raidz_aarch64_neonx2_impl` publishes the implementation as `"aarch64_neonx2"`.

## Architecture Configuration

The file is compiled only for `defined(__aarch64__)`. It includes `vdev_raidz_math_aarch64_neon_common.h`, defines stride/register macros, and then includes `vdev_raidz_math_impl.h`.

Compared with `aarch64_neon`, zero/copy/add use 8-vector strides and registers `0-7`, so those simple streaming operations process more data per loop body. Most syndrome and generation paths remain 4-vector stride operations. Two-column recovery for PQ, PR, and QR uses 4-vector recovery stride with separate X/Y/T register groups, while PQR recovery remains a 2-vector stride path.

## Special Build Handling

The file suppresses GCC's `-Wframe-larger-than=` diagnostic around `DEFINE_REC_METHODS(aarch64_neonx2)` for non-Clang GCC builds. The local comment explains that `-O0` debug builds may not coalesce stack frames enough, causing large-frame warnings even though the optimized build shape is intended.

## Dependencies

- `vdev_raidz_math_aarch64_neon_common.h` supplies all vector operations.
- `sys/vdev_raidz_impl.h` supplies RAID-Z structures and method-table types.
- `vdev_raidz_math_impl.h` supplies the shared generate/reconstruct implementation.

## Filesystem Relevance

This backend is an alternate AArch64 SIMD implementation for RAID-Z parity generation and reconstruction. It targets throughput improvements by increasing unrolling/register use for common buffer operations while preserving the same RAID-Z equations and selection gate as the baseline NEON backend.

## Correctness Notes

- Selection requires `kfpu_allowed()`.
- The x2 variant changes only macro configuration and generated code shape; it does not define independent parity equations.
- Larger unrolled recovery paths increase register and stack-pressure sensitivity, reflected in the explicit GCC diagnostic handling.
