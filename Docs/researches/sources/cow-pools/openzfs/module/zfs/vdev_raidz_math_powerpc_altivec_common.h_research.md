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
