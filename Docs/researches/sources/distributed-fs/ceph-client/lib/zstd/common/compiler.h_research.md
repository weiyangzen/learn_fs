# sources/distributed-fs/ceph-client/lib/zstd/common/compiler.h

Purpose: Centralizes compiler attributes, inlining macros, branch/prefetch hints, alignment helpers, fallthrough annotation, and sanitizer workarounds for kernel zstd code.

Important APIs/macros:
- Inline macros: `INLINE_KEYWORD`, `FORCE_INLINE_ATTR`, `FORCE_INLINE_TEMPLATE`, `HINT_INLINE`, `MEM_STATIC`, `FORCE_NOINLINE`.
- Target/prefetch macros: `TARGET_ATTRIBUTE`, `BMI2_TARGET_ATTRIBUTE`, `PREFETCH_L1`, `PREFETCH_L2`, `PREFETCH_AREA`.
- Optimization/control macros: `DONT_VECTORIZE`, `LIKELY`, `UNLIKELY`, `ZSTD_UNREACHABLE`, `ZSTD_FALLTHROUGH`.
- Alignment helpers: `ZSTD_isPower2`, `ZSTD_ALIGNOF`, `ZSTD_ALIGNED`.
- Pointer sanitizer helpers: `ZSTD_wrappedPtrDiff`, `ZSTD_wrappedPtrAdd`, `ZSTD_wrappedPtrSub`, `ZSTD_maybeNullPtrAdd`.

Control flow:
- Mostly preprocessor configuration based on compiler and target.
- Prefetch area loops over cache lines.
- Pointer helper functions isolate operations that intentionally rely on wrapping or NULL+0 behavior workarounds.

State and persistence: Stateless.

Dependencies and integration:
- Includes `<linux/types.h>` and `portability_macros.h`.
- Included across zstd common/compress/decompress code to keep upstream-like macros compatible with kernel builds.

Risks:
- Attribute and builtin checks must be accepted by the kernel compiler matrix.
- Pointer-overflow sanitizer exemptions are intentionally narrow; removing them can create false-positive UBSAN/ASAN reports in decompressor code.
- `ZSTD_FALLTHROUGH` maps to kernel `fallthrough`; include context must provide it.

Test signals:
- Build zstd under GCC and Clang, with sanitizers where supported.
- Cross-compile 32-bit, 64-bit, x86 BMI2-capable, and non-x86 targets.
