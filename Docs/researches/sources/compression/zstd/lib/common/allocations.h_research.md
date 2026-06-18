# sources/compression/zstd/lib/common/allocations.h

Purpose: centralizes zstd custom-memory allocation wrappers. It adapts the public `ZSTD_customMem` callback structure to internal allocation, calloc, and free calls with default fallbacks.

Important functions: `ZSTD_customMalloc`, `ZSTD_customCalloc`, and `ZSTD_customFree`, all `MEM_STATIC`. Dependencies expose `ZSTD_malloc`, `ZSTD_calloc`, `ZSTD_free`, and `ZSTD_memset`.

Control flow: malloc uses `customMem.customAlloc` when set, otherwise default allocator. calloc uses custom allocation plus explicit zeroing when custom allocation is supplied, otherwise default calloc. free ignores NULL; for non-NULL it uses `customFree` if present, otherwise default free.

State and persistence: no state. Ownership follows the allocator selected by the `ZSTD_customMem` value passed through contexts.

Dependencies/integration: includes `zstd_deps.h`, `compiler.h`, and static-linking-only `zstd.h` for `ZSTD_customMem`. Used by compression/decompression contexts that support caller-provided memory.

Risks: a partially configured `ZSTD_customMem` with custom allocation but missing matching free will allocate with the custom allocator and free with the default allocator, which is unsafe unless upstream validation prevents it. Custom calloc assumes the custom allocator returns memory suitable for `ZSTD_memset`.

Test signals: contexts with default allocator, full custom allocator/free pair, allocation failure, zero-size allocation behavior, and sanitizer checks for allocator mismatch.
