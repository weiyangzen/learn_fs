# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_ssse3.c

## Scope

x86-64 SSSE3 RAID-Z math backend plus the shared x86 carryless/nibble multiply lookup table. The executable backend uses SSSE3 `pshufb` to accelerate GF(2^8) multiplication for RAID-Z generation and reconstruction.

## Main Interfaces

- `vdev_raidz_ssse3_impl`: `raidz_impl_ops_t` backend named `ssse3`.
- `raidz_will_ssse3_work()`: enables the backend when SIMD is allowed and SSE, SSE2, and SSSE3 are available.
- `DEFINE_GEN_METHODS(ssse3)` and `DEFINE_REC_METHODS(ssse3)`: instantiate template methods.
- Template macro API: `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, `STORE`, `MUL2_SETUP`, `MUL2`, `MUL4`, `MUL`.
- `gf_clmul_mod_lt[4*256][16]`: 256-byte-aligned lookup table compiled for x86 when SSSE3, AVX2, or AVX512BW SIMD code may need it.

## State And Control Flow

The SSSE3 backend section is compiled only under `defined(__x86_64) && HAVE_SIMD(SSSE3)`. Like SSE2, it defines a 16-byte aligned `v_t` and uses inline XMM assembly for load/store/copy/XOR operations. Unsupported register counts call `ZFS_ASM_BUG()`.

`MUL2()` still uses byte doubling and the `0x1d` reduction mask, but general multiplication differs from SSE2. `_MULx2(c, ...)` splits each byte into high and low nibbles, loads four 16-byte rows for coefficient `c` from `gf_clmul_mod_lt`, uses `pshufb` to select nibble products/reduction terms, and XORs the upper/lower partial results back into two XMM registers. `MUL(c, ...)` handles either two or four registers by applying `_MULx2()` to register pairs.

The operation binding section gives SSSE3 wider coverage than SSE2 for general multiply: `MUL_STRIDE` is 4, and PQR reconstruction uses two-register groups for `X`, `Y`, `Z`, `XS`, and `YS`. This reflects the more efficient table-shuffle multiply path.

After method instantiation, the file defines the backend registration with no init/fini hooks. The large `gf_clmul_mod_lt` table follows outside the SSSE3-only backend guard but inside an x86 guard that also includes AVX2 and AVX512BW consumers. The table is static constant data, grouped as four 16-byte rows per coefficient.

## Dependencies

Depends on `sys/isa_defs.h`, `sys/simd.h`, `sys/vdev_raidz_impl.h`, `vdev_raidz_math_impl.h`, kernel FPU/SIMD helpers, and x86 SSSE3 `pshufb` semantics. The table is also a cross-file dependency for wider x86 RAID-Z math implementations.

## Correctness Notes

The `gf_clmul_mod_lt` layout is tightly coupled to `_MULx2()` and to other x86 SIMD backends that reuse the table. Its 256-byte alignment matters for predictable indexed loads and cache behavior. The macro layer assumes 16-byte alignment and exact XMM scratch-register usage (`xmm10..xmm15`); accidental register overlap would break multiplication. Runtime support checks must prevent use outside safe SIMD contexts.
