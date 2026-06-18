# sources/compression/zstd/tests/fuzz/fuzz_helpers.h

## Purpose

`fuzz_helpers.h` is the common C/C++ header for zstd fuzz targets. It centralizes always-on assertions, small utility macros, and allocation/comparison helper declarations so libFuzzer targets fail loudly on invariant violations even in release-style builds.

## Important APIs, Types, And Macros

The public surface is intentionally compact: `FUZZ_malloc()`, `FUZZ_malloc_rand()`, and `FUZZ_memcmp()` are declared for fuzz harness allocation and NULL-tolerant comparison. `FUZZ_ASSERT_MSG()`, `FUZZ_ASSERT()`, and `FUZZ_ZASSERT()` abort on failed predicates or zstd error codes; `FUZZ_ZASSERT()` converts zstd error returns through `ZSTD_getErrorName()`.

`MIN()` and `MAX()` provide local arithmetic helpers used across the fuzz directory. `FUZZ_STATIC` normalizes an unused static-inline declaration across GCC, C99/C++, MSVC, and fallback C compilers. `FUZZ_QUOTE()` stringifies assertion expressions for diagnostics.

## Control Flow

The header itself has no runtime control flow beyond assertion macro expansion. A failed `FUZZ_ASSERT_MSG()` writes file, line, condition text, and an optional message to `stderr`, then calls `abort()`. Successful assertions evaluate to a no-op expression. Callers are expected to use `FUZZ_ZASSERT()` immediately after zstd API calls whose successful result is required for the current fuzz invariant.

## State And Persistence

This file owns no persistent state. It depends on the implementation of the declared helpers elsewhere in the fuzz support code. Allocation semantics matter: `FUZZ_malloc()` may return `NULL` for size zero, while `FUZZ_malloc_rand()` may return a random pointer for size zero and warns callers to free only when the requested size was positive.

## Dependencies And Integration Points

It includes zstd fuzz infrastructure (`fuzz.h`, `fuzz_data_producer.h`), diagnostics (`debug.h`), hashing (`xxhash.h`), and the public zstd API (`zstd.h`). It is included by most fuzz targets in this directory and forms the bridge between arbitrary fuzzer inputs and hard process-failing correctness checks.

## Risks And Edge Cases

`MIN()` and `MAX()` evaluate arguments more than once, so callers must avoid side effects. `FUZZ_malloc_rand()` intentionally permits invalid-looking zero-size pointers, so consumers must preserve the size guard when freeing. Because assertions call `abort()`, any false positive invariant or unexpected zstd error becomes a crash signal in fuzzing and regression replay.

## Test Signals

The useful signal is indirect: fuzz targets using this header should crash with readable diagnostics on corruption, bad zstd return codes, allocation failures, or mismatched round trips. Compiler coverage should include C and C++ builds, GCC/Clang/MSVC-style inline handling, and zero-size allocation paths.
