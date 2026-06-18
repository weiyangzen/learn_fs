# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx2.c

## Scope

This file implements the x86_64 AVX2 RAID-Z math primitive layer, configures the shared RAID-Z math template for 32-byte vectors, and registers the `"avx2"` backend.

The source was read completely, lines 1-415.

## Primary Interfaces

- `v_t` is a 32-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` map to AVX2 `ymm` instructions.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF arithmetic.
- `DEFINE_GEN_METHODS(avx2)` and `DEFINE_REC_METHODS(avx2)` instantiate the shared methods.
- `raidz_will_avx2_work()` requires `kfpu_allowed()`, `zfs_avx_available()`, and `zfs_avx2_available()`.
- `vdev_raidz_avx2_impl` registers the backend as `"avx2"`.

## Vector Operations

The implementation uses `ymm` registers and 32-byte memory slots:
- `vpxor` implements XOR and XOR-accumulate.
- `vmovdqa` implements aligned loads, stores, and copies.
- `ZERO` is implemented as `XOR(r, r)`.
- `FLUSH()` issues `vzeroupper`, and `raidz_math_end()` calls it before `kfpu_end()` to avoid AVX/SSE transition costs and stale upper-register state.

Unsupported register counts call `ZFS_ASM_BUG()`/`ASSERT(0)`.

## GF Multiplication

`MUL2_SETUP()` broadcasts `0x1d` into `ymm14` and zeros `ymm15`. `_MUL2()` uses signed byte compare, byte add, mask, and XOR reduction to multiply by 2 in GF(2^8). `MUL4()` calls `MUL2()` twice.

Arbitrary `MUL(c, ...)` uses the externally defined `gf_clmul_mod_lt` table. `_MULx2()` broadcasts the coefficient's 16-byte subtables into AVX lanes, separates upper and lower nibbles with a `0x0f` mask, performs `vpshufb` table lookups, and XORs partial products. Four-vector multiplication is handled as two two-vector operations.

## Template Configuration

All generation, syndrome, and simple buffer helpers are configured with stride 4. Two-column and three-column reconstruction use 2-vector recovery strides and register groups matching the generic `vdev_raidz_math_impl.h` recovery callbacks.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX2)`.
- `sys/simd.h` supplies CPU feature probes and FPU-state wrappers.
- `gf_clmul_mod_lt` is provided by the AArch64 NEON table file.
- `vdev_raidz_math_impl.h` supplies shared RAID-Z algorithms.

## Filesystem Relevance

This is the AVX2 acceleration backend for ZFS RAID-Z P/Q/R parity generation and reconstruction on x86_64. It processes ABD buffers in vector chunks while the shared template handles RAID-Z row geometry, parity-column ordering, and failed-column equations.

## Correctness Notes

- The backend must not be selected unless both AVX and AVX2 are available and kernel FPU use is allowed.
- Loads/stores use aligned AVX instructions, so the surrounding ABD RAID-Z iteration must provide appropriately aligned vector spans.
- The arbitrary multiplication path depends on `gf_clmul_mod_lt` layout and on `vpshufb` operating independently per 128-bit lane.
