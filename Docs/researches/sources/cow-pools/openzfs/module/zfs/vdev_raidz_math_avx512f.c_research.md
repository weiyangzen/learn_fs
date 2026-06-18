# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_avx512f.c

## Scope

This file implements an x86_64 AVX512F RAID-Z math backend for systems with AVX512F but without relying on AVX512BW byte shuffle/table operations. It uses 64-byte vectors and builds arbitrary GF multiplication from generated per-coefficient functions.

The source was read completely, lines 1-495.

## Primary Interfaces

- `v_t` is a 64-byte aligned vector element.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` use `zmm` operations.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF multiplication without the shared lookup table.
- `MUL_x2_DEFINE(0..255)` emits 256 static multiplication functions.
- `gf_x2_mul_fns[256]` maps coefficient values to those generated functions.
- `DEFINE_GEN_METHODS(avx512f)` and `DEFINE_REC_METHODS(avx512f)` instantiate shared RAID-Z methods.
- `raidz_will_avx512f_work()` requires `kfpu_allowed()`, AVX, AVX2, and AVX512F availability.
- `vdev_raidz_avx512f_impl` registers the backend as `"avx512f"`.

## Vector Operations

The file uses `zmm` registers for primary operations and defines `VRy*` helpers for `ymm` names, though the active RAID-Z primitives are expressed with `zmm` macros. `vpxorq` performs XOR, `vmovdqa64` performs aligned movement, and `ZERO` is implemented as self-XOR.

Unlike the AVX512BW file, some switch statements omit explicit default assertions for unsupported counts in simple operations. The generated template's macro configuration supplies the supported counts used by these paths.

## GF Multiplication

`MUL2_SETUP()` broadcasts constants used by the AVX512F-only multiply-by-2 routine: reduction byte `0x1d`, high-bit mask `0x80`, and low-bit mask `0xfe`. `_MUL2()` uses qword logical shifts and `vpternlogd` to emulate byte-wise GF multiply-by-2 without AVX512BW byte compare/masked-byte operations.

Arbitrary multiplication is implemented by `_MUL_PARAM(x, in, acc)`, which conditionally accumulates powers of two for each coefficient bit. `MUL_x2_DEFINE()` expands this logic into 256 coefficient-specific functions. `MUL(c, ...)` copies two-vector pairs into fixed scratch registers, calls `gf_x2_mul_fns[c]`, and copies the accumulated result back.

## Template Configuration

Generation, syndrome, zero/copy/add, and multiply paths use stride 4. Unlike AVX2 and AVX512BW, reconstruction paths for PQ, PR, QR, and PQR are also configured with stride 4 and larger register groups. Recovery `*_DEFINE()` macros call `MUL2_SETUP()` where arbitrary multiplication may require the AVX512F constants.

## Dependencies

- Compiled only when `defined(__x86_64) && HAVE_SIMD(AVX512F)`.
- `sys/simd.h` supplies CPU feature probes and FPU state wrappers.
- `sys/debug.h` supplies `VERIFY()`.
- `vdev_raidz_math_impl.h` supplies the shared RAID-Z algorithms.
- This file does not consume `gf_clmul_mod_lt`; it uses generated multiply functions instead.

## Filesystem Relevance

This backend provides RAID-Z SIMD acceleration for AVX512F-capable systems where AVX512BW-specific byte operations may not be available. It keeps ZFS RAID-Z parity/reconstruction accelerated using only AVX512F plus AVX/AVX2 prerequisites.

## Correctness Notes

- The generated 256-function table must preserve GF(2^8) multiplication semantics for every coefficient.
- Runtime selection requires AVX2 as well as AVX512F, reflecting dependencies in the instruction strategy and SIMD environment.
- Register scratch choices such as `_mul_x2_in` and `_mul_x2_acc` are part of the macro contract used by generated multiplication functions.
