# Group Research: group_1449_openzfs_sources_cow_pools_openzfs_module_zfs_vdev_raidz_math_powerp_0de0890afb39

Scope: `Docs/research_subset_a.md` includes `sources/cow-pools/openzfs`. All listed source files were read completely.

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec.c -->
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
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec.c -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec_common.h -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec_common.h

## Scope

Shared PowerPC AltiVec macro implementation for RAID-Z math templates. This header defines vector register plumbing, load/store/XOR/copy/zero primitives, GF multiply-by-2 and multiply-by-constant operations, SIMD begin/end hooks, and vector variable declarations consumed by `vdev_raidz_math_impl.h`.

## Main Interfaces

- Register/constraint helpers: `VR*`, `RVR*`, `WVR*`, `UVR*`, `REG_CNT()`, `R_01()`, `R_23()`.
- Vector memory and logic primitives: `XOR_ACC()`, `XOR()`, `ZERO()`, `COPY()`, `LOAD()`, `STORE()`.
- GF arithmetic primitives: `MUL2_SETUP()`, `MUL2()`, `MUL4()`, `_MULx2()`, `MUL()`.
- SIMD context hooks: `raidz_math_begin()` maps to `kfpu_begin()`, `raidz_math_end()` maps to `kfpu_end()`.
- Vector declarations: `GEN_X_DEFINE_*()` macros declare 16-byte vector variables for the template-generated routines.
- External data dependency: `extern const uint8_t gf_clmul_mod_lt[4*256][16]`.

## State And Control Flow

The header uses GCC vector variables and inline AltiVec assembly. `v_t` is a 16-byte aligned byte vector wrapper, and `ELEM_SIZE` is fixed at 16. `OFFSET()` computes byte offsets for vector loads and stores.

The memory primitives specialize for 2, 4, or 8 vector registers. `LOAD()` and `STORE()` use `lvx` and `stvx`; `XOR_ACC()` loads source vectors into temporary registers and XORs them into accumulators; `ZERO()` self-XORs vectors; `COPY()` uses `vor` as a vector move.

`MUL2_SETUP()` prepares the field reduction constants in vector registers. `MUL2()` doubles each byte in GF(2^8) by shifting with `vaddubm`, detecting high bits with signed byte compare, and XORing the `0x1d` reduction polynomial where needed. `MUL4()` applies `MUL2()` twice.

`MUL(c, ...)` multiplies vectors by a constant using `_MULx2()` in pairs. `_MULx2()` splits input bytes into high and low nibbles, uses `vperm` into four `gf_clmul_mod_lt` rows for the coefficient, and XORs the partial products and modular-reduction terms back into the result vectors.

The lower section provides two versions of vector variable declaration macros: a disabled kernel-oriented block with explicit register bindings, and the active generic block declaring `unsigned char` vectors with `vector_size(16)`. The AltiVec implementation file chooses subsets of these declarations for each generated RAID-Z operation.

## Dependencies

Depends on PowerPC AltiVec inline assembly, GCC vector extensions, `sys/simd.h`, OpenZFS kernel FPU helpers, and the `gf_clmul_mod_lt` table supplied by `vdev_raidz_math_powerpc_altivec.c`.

## Correctness Notes

The inline assembly constraints are carefully constructed to avoid duplicate register operands when a macro path uses fewer registers than the helper family supports. Unsupported register counts deliberately hit `ASSERT(0)`. The multiplication path assumes `gf_clmul_mod_lt` is correctly endian-matched and 16-byte addressable. `STORE()` declares a memory clobber, which is required because the compiler otherwise cannot see the inline assembly writes.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_powerpc_altivec_common.h -->

<!-- BEGIN FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_scalar.c -->
# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_scalar.c

## Scope

Portable scalar RAID-Z math backend. This file provides the always-available CPU implementation for RAID-Z parity generation and reconstruction, using native 32-bit or 64-bit words for XOR and bytewise lookup tables for GF(2^8) multiplication.

## Main Interfaces

- `raidz_init_scalar()`: initializes `vdev_raidz_mul_lt[256][256]` with `gf_mul(c, i)`.
- `raidz_will_scalar_work()`: always returns `B_TRUE`.
- `vdev_raidz_scalar_impl`: backend named `scalar`.
- `DEFINE_GEN_METHODS(scalar)` and `DEFINE_REC_METHODS(scalar)`: instantiate shared RAID-Z gen/rec functions.
- Public GF tables:
  - `vdev_raidz_pow2[256]`: powers of 2 in the RAID-Z field.
  - `vdev_raidz_log2[256]`: logarithms base 2 in the same field.

## State And Control Flow

The file chooses `ELEM_SIZE` and `iv_t` at compile time: 4-byte `uint32_t` on 32-bit-capable scalar width, or 8-byte `uint64_t` on 64-bit. The scalar vector type `v_t` is a union of one native integer and per-byte access.

XOR-style operations work over the full native integer: `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` are direct word operations. Multiplication by 2 is optimized with masks: high bits are detected, shifted into an all-byte reduction mask, bytes are shifted left while clearing cross-byte overflow, then the `0x1d` reduction polynomial is XORed where required. `MUL4()` applies that twice.

General multiply-by-constant uses `vdev_raidz_mul_lt[c]` and rewrites each byte independently through the lookup table. The table is initialized at backend init time from `gf_mul()`. The backend has no SIMD begin/end requirements.

The file maps the shared template’s operation-specific macros to one scalar element per stride: P/PQ/PQR generation, syndrome generation, and PQ/PR/QR/PQR reconstruction all declare the scalar temporaries needed by `vdev_raidz_math_impl.h`.

## Dependencies

Depends on `sys/vdev_raidz_impl.h`, shared RAID-Z template code in `vdev_raidz_math_impl.h`, `gf_mul()`, `zfs_fallthrough`, and OpenZFS RAID-Z field conventions encoded by `vdev_raidz_pow2` and `vdev_raidz_log2`.

## Correctness Notes

This is the fallback implementation and must be valid on both 32-bit and 64-bit targets. The native-word XOR path relies on `v_t` having exactly `ELEM_SIZE` bytes, while multiplication intentionally falls back to byte addressing because GF multiplication is per byte. `raidz_init_scalar()` must run before reconstruction paths that use `MUL(c, a)`. The log table encodes zero as `0`, so callers must handle true zero semantics according to the RAID-Z math equations rather than treating the log table as a general mathematical logarithm.
<!-- END FILE RESEARCH: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_scalar.c -->