# sources/compression/zstd/lib/common/cpu.h

Purpose: runtime x86 CPU feature detection wrapper adapted from folly. It exposes a `ZSTD_cpuid_t` register snapshot and static predicate functions for individual CPU features.

Important types/functions/macros: `ZSTD_cpuid_t` with `f1c`, `f1d`, `f7b`, `f7c`; `ZSTD_cpuid()`; generated predicates such as `ZSTD_cpuid_sse2`, `ZSTD_cpuid_popcnt`, `ZSTD_cpuid_avx`, `ZSTD_cpuid_bmi1`, `ZSTD_cpuid_avx2`, and `ZSTD_cpuid_bmi2`.

Control flow: `ZSTD_cpuid()` initializes feature registers to zero, then on supported MSVC/x86 or GCC/Clang x86 targets executes CPUID leaf 0 to determine max leaf, leaf 1 for base features, and leaf 7 for extended features. Special inline assembly protects reserved `rbx/ebx` in clang/MSVC and i386 PIC cases. Non-x86 targets return all-zero features. Predicate functions test one bit in the captured registers.

State and persistence: no cached global state; callers can store the returned snapshot if desired.

Dependencies/integration: includes `mem.h` and optional MSVC `<intrin.h>`. Used for dynamic dispatch decisions such as BMI2-optimized entropy/table routines.

Risks: inline assembly constraints are platform-sensitive. Returning zeros on non-x86 is safe but means callers must combine this with compile-time feature checks. OS support for AVX state is represented by feature bits but callers must interpret combinations correctly when using AVX instructions.

Test signals: x86 and non-x86 compile/runtime tests, PIC 32-bit builds, clang-cl/MSVC variants, feature predicate validation against known CPU capabilities, and dynamic dispatch fallback behavior.
