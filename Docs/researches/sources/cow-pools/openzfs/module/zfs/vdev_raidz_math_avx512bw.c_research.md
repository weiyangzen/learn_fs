# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512bw.c

## Scope

This file implements the x86_64 AVX512BW RAID-Z math primitive layer, configures the shared RAID-Z math template for 64-byte vectors, and registers the `"avx512bw"` backend.

The source was read completely, lines 1-414.

## Primary Interfaces

- `v_t` is a 64-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` use `zmm` operations.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement byte-wise GF arithmetic with AVX512BW support.
- `DEFINE_GEN_METHODS(avx512bw)` and `DEFINE_REC_METHODS(avx512bw)` instantiate shared generation and reconstruction methods.
- `raidz_will_avx512bw_work()` requires `kfpu_allowed()`, AVX, AVX512F, and AVX512BW feature availability.
- `vdev_raidz_avx512bw_impl` registers the backend as `"avx512bw"`.

## Vector Operations

The implementation uses 64-byte `zmm` vectors:
- `vpxorq` handles XOR and XOR-accumulate.
- `vmovdqa64` handles aligned copy/load/store.
- `ZERO` is implemented through XORing registers with themselves.
- `MUL2()` uses AVX512 mask registers from `vpcmpb` to conditionally apply the `0x1d` reduction byte after byte addition.

Unsupported register counts call `ZFS_ASM_BUG()`/`ASSERT(0)`.

## GF Multiplication

Arbitrary multiplication uses the same `gf_clmul_mod_lt[4*256][16]` table as AVX2 and AArch64 NEON. `_MULx2()` broadcasts 128-bit subtable rows with `vbroadcasti32x4`, masks/shifts nibbles, uses `vpshufb`, and XORs the lookup results. Four-vector multiplication is split into two two-vector operations.

## Template Configuration

The file explicitly notes that zero, copy, and multiply are already 2x unrolled, so AVX512 operation stride must not exceed 4 or a single step would exceed the 512-byte block size used by the template's iteration model. Generation and syndrome paths use stride 4; recovery paths use stride 2 for multi-target reconstruction.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX512BW)`.
- `sys/param.h`, `sys/types.h`, and `sys/simd.h` supply system and SIMD helpers.
- `gf_clmul_mod_lt` is provided externally.
- `vdev_raidz_math_impl.h` supplies the shared RAID-Z algorithms.

## Filesystem Relevance

This backend accelerates RAID-Z parity generation and recovery on x86_64 CPUs with AVX512BW. It is especially relevant for byte-granular GF arithmetic because AVX512BW provides the byte operations and masking needed for efficient wide-vector multiply-by-2 and lookup-based arbitrary multiplication.

## Correctness Notes

- Feature gating includes AVX512F and AVX512BW; AVX512F alone is not sufficient for this backend.
- The stride limit comment is a correctness/performance guard around the shared template's chunking assumptions.
- The implementation's table-based multiplication must stay consistent with the global GF lookup table layout.
