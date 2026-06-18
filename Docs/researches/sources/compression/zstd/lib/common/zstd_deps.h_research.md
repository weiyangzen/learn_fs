# sources/compression/zstd/lib/common/zstd_deps.h

## Purpose
`zstd_deps.h` is zstd's libc dependency abstraction layer. It centralizes the minimum standard headers and macros needed by the library so embedders can replace or constrain libc usage, especially for freestanding or custom-allocation builds.

## Important APIs, Types, and Functions
The common section supplies `NULL`, integer limits, `size_t`, and memory operations through `ZSTD_memcpy`, `ZSTD_memmove`, and `ZSTD_memset`. Optional feature blocks are enabled by `ZSTD_DEPS_NEED_MALLOC`, `ZSTD_DEPS_NEED_MATH64`, `ZSTD_DEPS_NEED_ASSERT`, `ZSTD_DEPS_NEED_IO`, and `ZSTD_DEPS_NEED_STDINT`. These expose `ZSTD_malloc`, `ZSTD_calloc`, `ZSTD_free`, `ZSTD_div64`, `assert()`, `ZSTD_DEBUG_PRINT`, and `intptr_t` respectively.

## Control Flow, State, and Persistence
The header has no runtime control flow or state. Behavior is compile-time selected through include guards and opt-in macros. On GCC 4+, memory operations use compiler builtins; otherwise they map to libc functions. On GNU-like platforms it may define `_GNU_SOURCE` before any standard header, because zstd's combined source mode can need `qsort_r()` declarations elsewhere.

## Dependencies and Integration Points
This header is included by common and compression modules such as `zstd_common.c`, `hist.h`, `fse_compress.c`, and `huf_compress.c`. It is the integration point for custom platform layers: replacing this file or predefining equivalent macros changes allocation, memory, math, debug IO, and assertion behavior across the library.

## Risks and Test Signals
The main risks are include-order sensitivity around `_GNU_SOURCE`, inconsistent macro overrides in custom builds, and assuming optional sections exist without defining the matching `ZSTD_DEPS_NEED_*` macro. Tests should compile minimal modules with only common dependencies, then with each optional block enabled. Freestanding builds should verify all required macros can be supplied without accidental libc references.
