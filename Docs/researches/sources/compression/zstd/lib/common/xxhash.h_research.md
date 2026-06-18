# Research: sources/compression/zstd/lib/common/xxhash.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-000309`: lines 1-7076, `Docs/researches/chunks/subset-b-000309_research.md`
- `subset-b-000310`: lines 7077-7094, `Docs/researches/chunks/subset-b-000310_research.md`

## Chunk Research

### subset-b-000309: lines 1-7076

# sources/compression/zstd/lib/common/xxhash.h lines 1-7076

## Scope And Purpose

This chunk covers almost the entire Zstandard-local copy of xxHash v0.8.2's single-header implementation. The file provides public declarations, optional static-linking state definitions, and, when `XXH_IMPLEMENTATION`, `XXH_INLINE_ALL`, or `XXH_PRIVATE_API` is active, function bodies for non-cryptographic hashing.

The Zstd adaptation at the top is important: it defines `XXH_NO_XXH3` unless a build overrides it and defines `XXH_NAMESPACE` to `ZSTD_` unless already provided. In the normal Zstd build, that means the active exported/linked symbols are the namespaced XXH32 and XXH64 families, such as `ZSTD_XXH64`, `ZSTD_XXH64_reset`, `ZSTD_XXH64_update`, and `ZSTD_XXH64_digest`. The large XXH3 declaration and implementation body remains in the file, but it is preprocessed out under the default `XXH_NO_XXH3` guard.

The immediate Zstd purpose is fast, stable, non-cryptographic hashing for frame content checksums, dictionary IDs/hash-table placement, long-distance matching fingerprints, tests, and tools. This is not a security primitive.

This chunk ends at line 7076 inside the disabled XXH3 implementation footer, immediately before the AVX2 GCC `#pragma GCC pop_options` and final closing guards. The merge lane should reconcile the last source lines 7077-7094 with this chunk if the final per-file report covers the whole header.

## Important APIs, Types, And Functions

Public stable declarations include:

- `XXH_versionNumber()` returning `XXH_VERSION_NUMBER` for version 0.8.2.
- `XXH_errorcode` with `XXH_OK` and `XXH_ERROR`.
- `XXH32_hash_t`, `XXH32()`, `XXH32_createState()`, `XXH32_freeState()`, `XXH32_copyState()`, `XXH32_reset()`, `XXH32_update()`, `XXH32_digest()`, `XXH32_canonicalFromHash()`, and `XXH32_hashFromCanonical()`.
- `XXH64_hash_t`, `XXH64()`, `XXH64_createState()`, `XXH64_freeState()`, `XXH64_copyState()`, `XXH64_reset()`, `XXH64_update()`, `XXH64_digest()`, `XXH64_canonicalFromHash()`, and `XXH64_hashFromCanonical()`.

Under `XXH_STATIC_LINKING_ONLY`, the header exposes the otherwise opaque streaming state layouts. `XXH32_state_s` stores a 32-bit total length modulo, a large-input marker, four accumulator lanes, a 16-byte partial buffer represented as `mem32[4]`, and reserved fields. `XXH64_state_s` stores a 64-bit total length, four accumulator lanes, a 32-byte partial buffer represented as `mem64[4]`, and reserved fields. Zstd defines `XXH_STATIC_LINKING_ONLY` in common headers where it embeds `XXH64_state_t` directly in compression/decompression contexts.

The implementation side defines portability helpers for allocation (`XXH_malloc`, `XXH_free`), copying (`XXH_memcpy`), unaligned 32/64-bit reads, little/big-endian conversion, byteswaps, rotations, assertions, compiler hints, and optional alignment-specific paths. `XXH_FORCE_MEMORY_ACCESS`, `XXH_FORCE_ALIGN_CHECK`, `XXH_SIZE_OPT`, `XXH_NO_INLINE_HINTS`, `XXH_NO_STREAM`, `XXH_NO_STDLIB`, and `XXH_CPU_LITTLE_ENDIAN` materially change generated code.

XXH32 uses primes `XXH_PRIME32_1` through `XXH_PRIME32_5`, `XXH32_round()` for 4-byte lane mixing, `XXH32_avalanche()` for final bit diffusion, `XXH32_finalize()` for the last 0-15 bytes, and `XXH32_endian_align()` for the one-shot 16-byte-stripe loop. The one-shot `XXH32()` may call the direct implementation or, when `XXH_SIZE_OPT >= 2` and streaming is enabled, route through the streaming API to reduce code size.

XXH64 mirrors the structure with 64-bit primes, `XXH64_round()`, `XXH64_mergeRound()`, `XXH64_avalanche()`, `XXH64_finalize()`, and `XXH64_endian_align()`. It processes 32-byte stripes across four 64-bit accumulators and handles tail chunks in 8-byte, 4-byte, and 1-byte stages.

Although normally disabled in Zstd, this chunk contains the bulk of XXH3 declarations and implementation under `#ifndef XXH_NO_XXH3`: `XXH3_64bits*`, `XXH3_128bits*`, `XXH128_hash_t`, canonical 128-bit helpers, state allocation/reset/update/digest functions, secret generation helpers, scalar and SIMD accumulation paths, and vector selection for AVX512, AVX2, SSE2, NEON, VSX, and SVE. If a build undefines `XXH_NO_XXH3`, all of that becomes part of the same namespaced header.

## Control Flow And Runtime Behavior

Normal linked Zstd behavior starts in `sources/compression/zstd/lib/common/xxhash.c`, which defines `XXH_STATIC_LINKING_ONLY` and `XXH_IMPLEMENTATION`, then includes this header. That causes the header to emit the function bodies once. Other Zstd translation units include the same header for declarations and state definitions.

For `XXH32(input, len, seed)`, the control flow is:

1. Optionally select an aligned-read path when `XXH_FORCE_ALIGN_CHECK` is active and `input` is 4-byte aligned.
2. For `len >= 16`, initialize four accumulator lanes from the seed and process 16-byte stripes as four little-endian 32-bit words.
3. For shorter inputs, initialize from `seed + XXH_PRIME32_5`.
4. Add the input length and finalize the remaining 0-15 bytes.
5. Avalanche the result.

`XXH32_update()` maintains equivalent state incrementally. It appends short input to the 16-byte internal buffer, completes a buffered stripe when possible, processes full 16-byte stripes into the four lanes, and stores any tail back into the state. `XXH32_digest()` computes the hash from a copy-like read of state fields and buffered bytes without mutating the state.

For `XXH64(input, len, seed)`, the flow is analogous but with 32-byte stripes, 64-bit lane reads, an extra merge of each lane into the final accumulator, and tail handling for 8-byte, 4-byte, then byte chunks. `XXH64_update()` and `XXH64_digest()` provide the streaming equivalent.

Canonical conversion functions convert native integer hash values to fixed big-endian byte arrays and back. This is the portable representation used when hashes need to be serialized or compared independent of host endianness.

For the disabled XXH3 path, the intended control flow is length-tiered: 0-16, 17-128, 129-240, and long-input modes. Long mode accumulates 64-byte stripes into 8 lanes using a selected scalar/SIMD backend, periodically scrambles accumulators with secret material, and merges accumulators into 64-bit or 128-bit outputs. Streaming XXH3 buffers up to 256 bytes and digests from a local accumulator copy so digest does not alter the stream state.

## State And Persistence Behavior

The one-shot XXH32 and XXH64 functions are stateless. Their only observable output is the returned hash.

Streaming state is caller-owned after allocation or embedding. `XXH*_createState()` allocates with the header's local `XXH_malloc()` wrapper, and `XXH*_freeState()` frees with `XXH_free()`. In `XXH_NO_STDLIB` builds, allocation stubs return `NULL`, so embedded/static state is required. Zstd commonly embeds `XXH64_state_t` in contexts such as compression, decompression, legacy decompression, tests, and sequence generators.

`XXH*_reset()` zeroes and seeds state for a new stream. `XXH*_update()` mutates counters, accumulator lanes, partial buffers, and buffer sizes. `XXH*_digest()` does not mutate state, which lets callers digest midstream and continue updating.

There is no file I/O, environment access, global mutable state, or persistent storage in the active XXH32/XXH64 implementation. Hash stability across versions is nevertheless a persistence contract for serialized frame checksums, dictionary IDs, test data stamps, and any other stored hashes.

The disabled XXH3 path would introduce a static default secret table, aligned heap allocation for `XXH3_state_t`, generated per-seed secrets stored in state, and external-secret references that must outlive a streaming session. Those risks are dormant in the default Zstd build but relevant if XXH3 is enabled.

## Dependencies And Integration Points

The header depends on standard C headers selected by feature guards: `stddef.h`, `stdint.h` or legacy integer fallbacks, `limits.h`, `string.h`, and optionally `stdlib.h`. The disabled XXH3 code additionally conditionally includes architecture intrinsic headers such as `immintrin.h`, `emmintrin.h`, `arm_neon.h`, `arm_sve.h`, `altivec.h`, and `s390intrin.h`.

The main integration point is `sources/compression/zstd/lib/common/xxhash.c`, which instantiates the implementation. Build files also define or preserve `XXH_NAMESPACE=ZSTD_`, and the header itself supplies that namespace default as a local adaptation. `XXH_INLINE_ALL` and `XXH_PRIVATE_API` support header-only/private embedding but are not the normal libzstd path.

Zstd integrations include:

- `zstd_internal.h`, which defines `XXH_STATIC_LINKING_ONLY` before including this header so internal contexts can store `XXH64_state_t`.
- Compression paths in `zstd_compress.c` and `zstdmt_compress.c`, which reset/update/digest `XXH64` state to write 32-bit frame content checksums from the low 32 bits of the 64-bit hash.
- Decompression paths in `zstd_decompress.c`, which reset/update/digest `XXH64` state to validate frame checksums and report `checksum_wrong` on mismatch.
- Dictionary and decompression hash tables, such as `ZSTD_DDictHashSet_getIndex()`, which use `XXH64()` over dictionary IDs.
- Dictionary builder and long-distance matching code, which use `XXH64()` for dictionary IDs and match fingerprints.
- Tests and tools, including `zstreamtest`, `seqgen`, `benchzstd`, `paramgrill`, regression data hashing, and crash repro tests that use XXH32/XXH64 as deterministic checks.

## Risks And Edge Cases

The most important correctness risk is hash stability. Changing constants, endian reads, tail processing, namespace behavior, or streaming state layout can silently alter frame checksums, dictionary IDs, test fixtures, and tool outputs.

The API accepts `input == NULL` only when `len == 0`; otherwise behavior is invalid except for debug assertions. Several update paths return `XXH_OK` for `NULL, 0`, so callers must not rely on runtime validation for bad nonzero lengths.

State pointers are assumed valid for reset/update/digest/copy APIs. Many functions assert rather than return errors for null state in active XXH32/XXH64 paths. Embedded state must be reset before use.

Unaligned memory behavior is controlled by `XXH_FORCE_MEMORY_ACCESS`. The default prefers packed/aligned(1) loads on many GCC/Clang targets, with comments explaining that some modes rely on implementation-defined behavior. Porting to strict-alignment or unusual compilers should test both unaligned and aligned paths.

Endianness handling is central. Hash results are defined over little-endian input interpretation, while canonical representations are big-endian. Big-endian platforms, runtime endian detection fallback, and byteshift load mode need coverage because most commodity Zstd testing is little-endian.

`XXH_NO_STDLIB` changes allocation semantics: create-state APIs return `NULL` when streaming allocation is requested. Zstd's embedded-state use is compatible, but external users of the header may be surprised.

`XXH_STATIC_LINKING_ONLY` exposes internal state layouts with an explicit ABI warning. Zstd relies on this internally, so an upstream xxHash sync that changes fields requires all embedding code to be rebuilt consistently.

`XXH_NAMESPACE` must remain consistent between declarations and implementation. Removing or overriding the Zstd namespace can create symbol collisions with another xxHash copy linked into the same process.

The disabled XXH3 code is large and architecture-sensitive. If enabled, it brings strict 64-byte alignment requirements for `XXH3_state_t`, external-secret lifetime requirements, secret-size preconditions, compiler target pragmas, and many SIMD-specific code paths. This chunk's requested range stops immediately before a pragma pop, so partial-range review should not conclude that the full source footer is balanced without checking the final lines.

## Test Signals

Known-answer tests should cover `XXH32()` and `XXH64()` for empty input, `"123456789"`, short lengths 1-15/1-31, exact stripe lengths 16/32, stripe length plus tails, large multi-stripe buffers, and multiple nonzero seeds.

Streaming equivalence tests should compare `XXH32()`/`XXH64()` one-shot results to reset/update/digest results across many chunk boundaries, especially one byte at a time, just below and above 16 and 32 bytes, and after calling digest midstream before additional updates.

Frame-level Zstd tests should verify compression with content checksums enabled, decompression checksum validation, checksum mismatch detection, streaming decompression checksum updates, and multithreaded compression checksum finalization. Existing `zstreamtest`, CLI `--check` behavior, regression data hash checks, and fuzzer checks are relevant signals.

Portability tests should build with representative macro combinations: default implementation, `XXH_FORCE_MEMORY_ACCESS=0` and `3`, `XXH_FORCE_ALIGN_CHECK=1`, `XXH_SIZE_OPT=1` and `2`, `XXH_NO_STDLIB`, `XXH_NO_STREAM`, and a big-endian target or emulator. The active code should also be compiled as C and C++ because of `extern "C"` and attribute handling.

Namespace/linkage tests should confirm public symbols are emitted with `ZSTD_` prefixes from `xxhash.c` and that another xxHash copy can coexist in the same link without collisions.

If a future Zstd build enables XXH3, additional test signals are required: short/midsize/long known-answer vectors for 64-bit and 128-bit variants, secret and seed variants, streaming equivalence, aligned-state allocation/freeing, external-secret lifetime assumptions in callers, and architecture-specific SIMD/scalar consistency.

### subset-b-000310: lines 7077-7094

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
