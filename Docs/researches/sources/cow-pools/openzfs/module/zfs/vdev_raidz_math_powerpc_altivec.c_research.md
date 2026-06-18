# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec.c

## Scope

PowerPC AltiVec RAID-Z math backend registration and lookup-table data. This file wires the shared RAID-Z math template to the PowerPC AltiVec helper macros, exposes the `powerpc_altivec` implementation, and defines endian-specific `gf_clmul_mod_lt` tables used by vector GF(2^8) multiplication.

## Main Interfaces

- `vdev_raidz_powerpc_altivec_impl`: `raidz_impl_ops_t` backend named `powerpc_altivec`.
- `raidz_will_powerpc_altivec_work()`: enables the backend only when `kfpu_allowed()` and `zfs_altivec_available()` are true.
- `DEFINE_GEN_METHODS(powerpc_altivec)` and `DEFINE_REC_METHODS(powerpc_altivec)`: instantiate generation and reconstruction entry points from `vdev_raidz_math_impl.h`.
- `gf_clmul_mod_lt[4*256][16]`: 256-byte-aligned lookup table consumed by the AltiVec common header’s `MUL()` path.

## State And Control Flow

The file is active only under `defined(__powerpc__)`; it applies `#pragma GCC target("altivec")`, includes `vdev_raidz_math_powerpc_altivec_common.h`, then defines per-operation register allocation and stride macros before including the shared RAID-Z math implementation.

Simple operations use four-lane vector strides: zero, copy, add, multiply, and P generation use registers `0..3` plus scratch registers `33..36`. PQ/PQR generation and syndrome passes add coefficient and scratch vector registers. Recovery paths use two-vector strides and declare additional temporaries for missing-data solving.

After method instantiation, the backend advertises `.init = NULL` and `.fini = NULL` because the large multiplication lookup data is statically compiled. The runtime support gate prevents use unless kernel FPU/SIMD context and AltiVec are available.

Most of the file is generated constant data. It defines one little-endian `gf_clmul_mod_lt` table under `defined(_ZFS_LITTLE_ENDIAN) && _LITTLE_ENDIAN`, and an alternate table under the `#else` branch for the other PowerPC endian configuration. Each table has `4 * 256` rows of 16 bytes and is aligned to 256 bytes for efficient indexed vector loads.

## Dependencies

Depends on OpenZFS RAID-Z implementation headers, the PowerPC AltiVec common macro layer, `kfpu_allowed()`, `zfs_altivec_available()`, and the shared `vdev_raidz_math_impl.h` template that expands the macro vocabulary into actual gen/rec functions.

## Correctness Notes

The operation macro definitions must match the expectations of `vdev_raidz_math_impl.h`; wrong stride or register tuple definitions would corrupt parity or reconstruction output. The endian split is significant because AltiVec byte permutation and table-index behavior differ by lane ordering. The support predicate is also correctness-critical: these routines use SIMD/FPU state and must not run when the kernel cannot safely enter that context.
