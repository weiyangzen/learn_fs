# sources/distributed-fs/ceph-client/tools/perf/util/demangle-rust-v0.h

## Purpose
This header defines perf's public C interface for Rust symbol demangling. It documents the borrowed-data contract for `struct demangle`, the supported demangling styles, and the bounded-output behavior expected by callers.

## Important APIs And Types
`enum demangle_style` distinguishes unknown, legacy, and v0 Rust formats. `struct demangle` contains the selected style, the mangled slice, original string slice, suffix slice, and legacy element count. `overflow_status` reports whether display fit the caller's buffer. `OVERFLOW_MARGIN` intentionally forces a few spare bytes so display can safely terminate and detect near-overflow. `DEMANGLE_NODISCARD` marks the display API's return value as important on GCC/Clang.

## Control Flow And Integration
Callers use `rust_demangle_demangle(const char *s, struct demangle *res)` to classify a NUL-terminated symbol, optionally check `rust_demangle_is_known(res)`, and then call `rust_demangle_display_demangle(res, out, len, alternate)`. The `alternate` flag maps to Rust's less verbose `{:#}` formatting style, omitting symbol hashes and some constant integer type suffixes.

## State, Dependencies, And Persistence
The header depends only on `<stddef.h>` and C/C++ linkage guards, but it uses `bool` in prototypes and therefore relies on consumers including or otherwise providing `<stdbool.h>` in C builds, as the implementation does. `struct demangle` contains borrowed pointers into the input symbol and does not own memory or persist beyond that input's lifetime.

## Risks And Test Signals
The highest integration risk is misuse of `struct demangle` after freeing or mutating the original symbol. Callers must also honor `OverflowOverflow` and retry with a larger buffer rather than assuming truncation. Compile tests should include C and C++ consumers, and behavioral tests should assert unknown-style passthrough, legacy/v0 classification, suffix preservation, and alternate formatting.
