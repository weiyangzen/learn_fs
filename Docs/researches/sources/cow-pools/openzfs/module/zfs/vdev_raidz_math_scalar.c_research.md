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
