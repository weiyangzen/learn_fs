# sources/compression/zstd/lib/common/xxhash.h lines 7077-7094

## Scope And Purpose

This chunk covers the final implementation guards at the end of Zstandard's vendored `xxhash.h`. The requested lines are not hash algorithm logic themselves; they close conditional compilation state opened earlier in the same header. They pop a GCC optimization override used for the AVX2 XXH3 implementation, close the C++ `extern "C"` block, and terminate the implementation-side feature guards for long-long support, XXH3 support, and `XXH_IMPLEMENTATION`.

In this Zstandard copy, the file starts with local adaptations that define `XXH_NO_XXH3` unless the embedding build already changed it. As a result, normal Zstd builds do not compile the XXH3 implementation block that these lines terminate. The chunk still matters because the header remains a full xxHash implementation when configured to expose XXH3, and because mismatched guards or pragmas here would break compilation of the whole compression library.

## Important APIs, Types, And Functions

No public callable API is defined in lines 7077-7094. The immediately preceding implementation API is `XXH3_generateSecret_fromSeed(void* secretBuffer, XXH64_hash_t seed)`, which creates a default-sized XXH3 secret from a seed and copies it into a caller-provided buffer. The requested chunk begins after that function body and closes the implementation environment it lives in.

The important symbols in this range are preprocessor controls:

- `XXH_VECTOR` selects the XXH3 vector backend. `XXH_AVX2` is the x86 AVX2 implementation selected earlier when `__AVX2__` is available, unless the caller overrides `XXH_VECTOR`.
- `__GNUC__` and `!defined(__clang__)` restrict the pragma pair to GCC. Clang also defines `__GNUC__`, so the explicit Clang exclusion prevents applying GCC-only optimization control to Clang.
- `__OPTIMIZE__` ensures the override is only used during optimized builds. It is intentionally not applied under `-O0`.
- `XXH_SIZE_OPT <= 0` avoids the override for size-optimized builds such as `-Os`/`-Oz`, matching the comment that the block respects debug and size builds.
- `#pragma GCC pop_options` restores GCC compiler options after the matching earlier `#pragma GCC push_options` and `#pragma GCC optimize("-O2")`.
- `defined(__cplusplus)` closes the `extern "C"` block, preserving C linkage for the C API when this header is included by C++ translation units.
- `XXH_NO_LONG_LONG`, `XXH_NO_XXH3`, and `XXH_IMPLEMENTATION` are the feature/implementation guards that decide whether this implementation tail is visible at all.

The `@}` Doxygen marker closes the current documentation group before the final `XXH_IMPLEMENTATION` guard closes.

## Control Flow

Runtime control flow is absent in the requested lines. The behavior is entirely compile-time:

1. Earlier in the implementation section, if the build is GCC, AVX2, optimized, and not size-optimized, the header pushes the current GCC options and forces `-O2` around the XXH3 implementation.
2. Lines 7077-7081 test the exact same condition and pop those options. This balances the compiler-option stack only when it was pushed.
3. Lines 7084-7086 close the C++ linkage block if the implementation section was compiled as C++.
4. Lines 7088-7089 close the implementation branches guarded by `XXH_NO_LONG_LONG` and `XXH_NO_XXH3`.
5. Lines 7091-7094 close the Doxygen group and the outer `XXH_IMPLEMENTATION` section.

The most important control-flow property is symmetry: the condition around `#pragma GCC pop_options` must remain equivalent to the earlier `push_options` condition. If one side changes without the other, GCC can diagnose an unmatched pragma stack, or subsequent code in the including translation unit can inherit unintended optimization settings.

## State And Persistence Behavior

This chunk has no runtime state, heap allocation, file I/O, or persistent data. Its state is compiler state: GCC's option stack is restored by `#pragma GCC pop_options`.

The closure of `extern "C"` also affects symbol linkage state at compile time. If it were omitted or moved incorrectly, C++ translation units could see later declarations with unintended C linkage, or the header could become syntactically invalid.

Because this is a header-only implementation mode controlled by `XXH_IMPLEMENTATION` or related inline macros, the consequences of these lines can affect every translation unit that includes this file in implementation mode. There is no persistent runtime artifact beyond the object code emitted under the selected guards.

## Dependencies And Integration Points

This chunk depends on definitions established earlier in `xxhash.h`:

- Vector detection defines `XXH_SCALAR`, `XXH_SSE2`, `XXH_AVX2`, `XXH_AVX512`, `XXH_NEON`, `XXH_VSX`, and `XXH_SVE`, then assigns `XXH_VECTOR`.
- Tuning logic defines `XXH_SIZE_OPT`, defaulting to size optimization for `-Os`/`-Oz` and no size optimization otherwise.
- The implementation section opens an `extern "C"` block for C++ consumers.
- The XXH3 implementation is guarded out when `XXH_NO_LONG_LONG` or `XXH_NO_XXH3` is active.

The direct integration point is Zstandard's common compression code that includes this vendored `xxhash.h` for fast non-cryptographic hashing. Zstd namespaces the API through `XXH_NAMESPACE ZSTD_`, so compiled symbols are generally prefixed for internal use. The top of this vendored file also defines `XXH_NO_XXH3` by default, which means Zstd normally integrates the older XXH32/XXH64 surface and excludes the XXH3 block closed here.

The AVX2 pragma integration is compiler-specific. It exists because GCC's AVX2 XXH3 path benefits from an optimization override around the implementation body. The final `pop_options` prevents that override from leaking into later code in an including translation unit, which is particularly important for header implementation mode.

The C++ integration point is ABI-facing: all public `XXH_PUBLIC_API` declarations inside the implementation block must keep C linkage when included from C++, so callers can link against C-compiled objects or consistent namespaced C symbols.

## Risks And Edge Cases

The highest-risk maintenance issue is an asymmetric pragma condition. The `pop_options` condition must track the earlier `push_options` condition exactly: AVX2, GCC, not Clang, optimized, and `XXH_SIZE_OPT <= 0`. Any drift can produce an unmatched pop or leave `-O2` active after the header.

This file is used as an includable implementation header, so leaked compiler state can affect user or Zstd code that appears textually after the include. That failure mode is subtle because it may show up as changed code generation rather than a direct source error.

The C++ `extern "C"` close must stay paired with the implementation-side open. Moving guard endings above or below it can cause link-name changes or C++ syntax errors, especially when different combinations of `XXH_NO_XXH3`, `XXH_NO_LONG_LONG`, and `XXH_IMPLEMENTATION` are used.

The comments on lines 7088-7089 use the guard names in their disabled form, but the preprocessor condition earlier is `#ifndef` style. This is conventional in this file, yet easy to misread during edits. A maintainer should verify the matching opening guards rather than relying only on end comments.

In Zstd's adapted copy, `XXH_NO_XXH3` is defined by default near the top of the file. Changes that expose XXH3 in Zstd builds would suddenly compile a much larger set of code, including the AVX2 pragma path closed here, and should be validated across the compiler matrix.

The final `#endif /* XXH_IMPLEMENTATION */` closes a large implementation region. Accidental edits here can convert what should be declaration-only includes into implementation includes, or vice versa, causing duplicate definitions, missing symbols, or inline/API mismatches.

## Test Signals

Compile-only tests are the primary signal for this chunk. The header should compile in declaration-only mode and implementation mode from both C and C++ translation units.

Compiler-matrix tests should include GCC with AVX2 enabled and optimization enabled, because that is the only path that exercises both `#pragma GCC push_options` earlier and `#pragma GCC pop_options` in this chunk. The same matrix should include Clang with AVX2, GCC under `-O0`, and GCC under `-Os` to confirm the pragma condition is correctly skipped.

Feature-matrix tests should compile with default Zstd settings where `XXH_NO_XXH3` is active, and with a configuration that enables XXH3 so the guarded implementation tail is parsed. Builds should also cover a platform/configuration where `XXH_NO_LONG_LONG` is relevant, or at least confirm the guard remains syntactically balanced when long-long support is disabled.

C++ integration tests should include this header inside a C++ translation unit with `XXH_IMPLEMENTATION` active and call representative exported functions. The goal is to catch broken `extern "C"` balancing or symbol-linkage drift.

Runtime hash tests do not directly exercise these final preprocessor lines, but they provide regression coverage for builds that pass through them. Useful vectors include known-answer tests for `XXH32`, `XXH64`, and, when XXH3 is enabled, `XXH3_64bits`, `XXH3_128bits`, and secret-generation APIs such as `XXH3_generateSecret_fromSeed()`.
