# sources/distributed-fs/ceph-client/lib/zstd/common/zstd_deps.h

## Purpose
`zstd_deps.h` centralizes libc-like dependencies for the kernel Zstd port. It replaces memory routines, allocation, 64-bit division, assertions, debug printing, and intptr support with kernel-safe equivalents or stubs selected by `ZSTD_DEPS_NEED_*` feature macros.

## Important APIs and Macros
The common section includes Linux limits/stddef and maps `ZSTD_memcpy`, `ZSTD_memmove`, and `ZSTD_memset` to compiler builtins. With `ZSTD_DEPS_NEED_MALLOC`, `ZSTD_malloc()` and `ZSTD_calloc()` return `NULL`, while `ZSTD_free()` is a no-op. `ZSTD_DEPS_NEED_MATH64` provides `ZSTD_div64()` through `div_u64()`. `ZSTD_DEPS_NEED_ASSERT` maps `assert(x)` to `WARN_ON(!(x))`. `ZSTD_DEPS_NEED_IO` maps debug printing to `pr_debug()`.

## Control Flow and State
This header has only macro-selected definitions and one static helper for 64-bit division. There is no persistent state. The important behavioral decision is that dynamic allocation is intentionally unavailable, forcing callers to use static or externally supplied workspaces.

## Dependencies and Integration Points
It is included by nearly all common/compress entropy files before they need libc-like facilities. FSE normalization depends on `ZSTD_div64()`. Compression and decompression paths depend on the memory macros. Debug and assert behavior flows through `debug.h` into this dependency layer.

## Risks and Test Signals
The largest risk is accidental use of allocation APIs in code paths that expect upstream userspace Zstd semantics; in this tree they fail by design. `assert()` as `WARN_ON()` reports but does not necessarily abort, so debug-only invariants cannot be treated as hard production validation. Tests should include allocation-failure paths, workspace-only compression/decompression, 64-bit division correctness on 32-bit kernels, and debug builds with `DEBUGLEVEL` enabling assert and print dependencies.
