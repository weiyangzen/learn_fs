# sources/compression/zstd/lib/common/compiler.h

Purpose: central portability header for compiler attributes, inlining, prefetching, branch prediction, target attributes, SIMD feature macros, fallthrough annotations, alignment helpers, pointer-overflow sanitizer workarounds, and sanitizer poisoning declarations.

Important macros/functions: `INLINE_KEYWORD`, `FORCE_INLINE_ATTR`, `FORCE_INLINE_TEMPLATE`, `HINT_INLINE`, `MEM_STATIC`, `FORCE_NOINLINE`, `TARGET_ATTRIBUTE`, `BMI2_TARGET_ATTRIBUTE`, `PREFETCH_L1/L2`, `PREFETCH_AREA`, `DONT_VECTORIZE`, `LIKELY/UNLIKELY`, `ZSTD_UNREACHABLE`, SIMD feature macros, `ZSTD_FALLTHROUGH`, `ZSTD_ALIGNOF`, `ZSTD_ALIGNED`, `ZSTD_wrappedPtrDiff`, `ZSTD_wrappedPtrAdd`, `ZSTD_wrappedPtrSub`, and `ZSTD_maybeNullPtrAdd`.

Control flow: preprocessor branches select compiler-specific syntax for GCC/Clang/MSVC/IAR/C99/C++ and platform-specific intrinsics. SIMD headers are included only when compile-time features and `ZSTD_NO_INTRINSICS` permit. Sanitizer sections declare ASan/MSan APIs when relevant and disable workspace poisoning on MinGW.

State and persistence: no runtime persistence. It shapes code generation across almost every zstd translation unit.

Dependencies/integration: includes `portability_macros.h`, `<stddef.h>`, optional compiler intrinsic headers, and sanitizer declarations. It is foundational for common, compression, decompression, and entropy code.

Risks: macro definitions affect ABI/performance and must remain compatible with many compilers. Misdetected SIMD or target attributes can break builds. Wrapped pointer helpers intentionally suppress sanitizer findings for zstd algorithms that rely on pointer wrapping; misuse could hide real bugs. Global warning pragmas for MSVC can mask warnings outside narrow code regions.

Test signals: compile matrices across GCC/Clang/MSVC/IAR, C89/C99/C++ consumers, sanitizer builds, MinGW, x86/ARM/RISC-V feature combinations, and codegen/performance checks for hot inlined paths.
