# File Research: sources/cow-pools/openzfs/module/zfs/vdev_raidz_math_sse2.c

## Scope

x86-64 SSE2 RAID-Z math backend. This file supplies 16-byte XMM primitives and operation-specific macro bindings for the shared `vdev_raidz_math_impl.h` template, then registers the `sse2` RAID-Z generation/reconstruction implementation.

## Main Interfaces

- `vdev_raidz_sse2_impl`: `raidz_impl_ops_t` backend named `sse2`.
- `raidz_will_sse2_work()`: enables the backend only when kernel SIMD use is allowed and SSE/SSE2 are available.
- `DEFINE_GEN_METHODS(sse2)` and `DEFINE_REC_METHODS(sse2)`: instantiate RAID-Z gen/rec entry points from the shared template.
- SIMD macro API consumed by the template: `XOR_ACC`, `XOR`, `ZERO`, `COPY`, `LOAD`, `STORE`, `MUL2_SETUP`, `MUL2`, `MUL4`, `MUL`.
- Generated constant multiply helpers: `mul_x1_0..255`, `mul_x2_0..255`, plus `gf_x1_mul_fns[256]` and `gf_x2_mul_fns[256]`.

## State And Control Flow

The file is compiled only for `defined(__x86_64) && HAVE_SIMD(SSE2)`. It defines a 16-byte aligned `v_t` and maps logical vector operands to XMM register names through variadic register-selection macros.

Memory and logic operations are inline assembly over 1, 2, or 4 XMM registers depending on the template operation. Loads/stores use aligned `movdqa`, XORs use `pxor`, copies use `movdqa`, and zeroing is implemented as XOR with self. Unsupported register counts generally trip `VERIFY(0)`.

GF(2^8) multiply-by-2 is implemented with SSE2 byte arithmetic: `MUL2_SETUP()` loads the `0x1d` reduction mask into `xmm15`; `_MUL2_x1/_MUL2_x2` detect high bits with signed byte compares, double bytes with `paddb`, and XOR the reduction polynomial where required. `MUL4()` applies `MUL2()` twice.

General multiply-by-constant is implemented without SSSE3 shuffle tables. `_MUL_PARAM()` decomposes the constant into powers of two, repeatedly applies `MUL2()`, and XORs selected powers into an accumulator. The file emits 256 one-lane and 256 two-lane static helper functions, then dispatches through aligned function-pointer tables in `MUL(c, ...)`.

The lower macro section binds template operation strides and register tuples. P/PQ/PQR generation and syndrome paths use four-register strides where possible. General multiplication uses two-register stride, and PQR reconstruction is reduced to one-register stride because SSE2 lacks the more efficient SSSE3 nibble-table multiply.

## Dependencies

Depends on `sys/isa_defs.h`, `sys/simd.h`, `sys/debug.h`, `sys/vdev_raidz_impl.h`, `vdev_raidz_math_impl.h`, `kfpu_begin()/kfpu_end()`, `kfpu_allowed()`, `zfs_sse_available()`, and `zfs_sse2_available()`.

## Correctness Notes

The backend assumes aligned 16-byte buffers because it uses `movdqa`. The register tuple macros and stride declarations are part of the ABI with `vdev_raidz_math_impl.h`; a mismatch would silently corrupt parity or recovery math. SIMD context gating is required because the routines directly use XMM state in kernel context. Constant multiplication correctness depends on `_MUL_PARAM()` preserving the input/accumulator register convention used by the generated helper functions.
