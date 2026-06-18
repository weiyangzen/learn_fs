# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_aarch64_neon_common.h

## Scope

This header defines the AArch64 NEON vector primitive layer used by both AArch64 RAID-Z math implementations. It maps generic operations expected by `vdev_raidz_math_impl.h` onto inline assembly over 16-byte NEON vectors.

The source was read completely, lines 1-685.

## Primary Interfaces

- `v_t` is the vector element type, a 16-byte aligned byte array.
- `ELEM_SIZE` is `16`.
- `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, and `STORE` implement vector data movement and XOR.
- `MUL2_SETUP`, `MUL2`, `MUL4`, and `MUL` implement GF(2^8) multiplication.
- `raidz_math_begin()` and `raidz_math_end()` wrap the generated math in `kfpu_begin()`/`kfpu_end()`.
- `GEN_X_DEFINE_*` declare vector variables either pinned to NEON registers in kernel builds or as compiler vector variables outside `_KERNEL`.

## Register And Assembly Model

The header uses variadic register-list macros to select the correct operand names and constraints for 2-, 4-, and 8-vector operations. `VR*`, `RVR*`, `WVR*`, and `UVR*` build inline-assembly references and input/output constraints around variables named `w0`, `w1`, and so on.

The code deliberately supplies dummy high-numbered operands for unused positions because GCC still validates constraints in macro-expanded assembly alternatives. In kernel builds, some temporary declarations alias `v31` for otherwise-unused register names, which avoids illegal duplicate constraints in active paths.

## Vector Operations

- `XOR_ACC(src, r...)` loads vectors from `src` and XORs them into existing registers.
- `XOR(r...)` XORs the first half of a register list into the second half.
- `ZERO(r...)` clears each listed vector by XORing it with itself.
- `COPY(r...)` copies the first half of a register list to the second half.
- `LOAD(src, r...)` loads contiguous 16-byte vectors from memory.
- `STORE(dst, r...)` writes contiguous 16-byte vectors to memory.

Unsupported register counts call `ZFS_ASM_BUG()`, which maps to `ASSERT(0)`.

## GF Multiplication

`MUL2_SETUP()` initializes a zero vector and a vector filled with the RAID-Z reduction polynomial byte `0x1d`. `MUL2()` performs byte-wise multiply by 2 using compare, shift, mask, and XOR reduction. `MUL4()` applies `MUL2()` twice.

Arbitrary constant multiplication uses the external `gf_clmul_mod_lt[4*256][16]` lookup table. `_MULx2(c, ...)` splits two vectors into upper and lower nibbles, uses NEON `tbl` lookups against the four subtables for coefficient `c`, and XORs the partial products. `MUL(c, ...)` applies `_MULx2()` to either one or two vector pairs.

## Dependencies

- `sys/types.h` provides fixed-width types.
- `sys/simd.h` provides kernel SIMD/FPU state helpers.
- `gf_clmul_mod_lt` is defined by `vdev_raidz_math_aarch64_neon.c`.

## Filesystem Relevance

The header is the hardware abstraction layer that lets the shared RAID-Z math template express parity and reconstruction in terms of vector primitives. It is performance critical because every RAID-Z P/Q/R operation on the AArch64 NEON backends expands through these macros.

## Correctness Notes

- The generated template assumes vector sizes and strides match `sizeof (v_t)`.
- The table multiplication path depends on the exact four-subtable layout from `gf_clmul_mod_lt`.
- The assembly uses explicit NEON registers and clobbers; edits must preserve GCC/Clang constraint validity as well as arithmetic behavior.
