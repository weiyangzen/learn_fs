# sources/compression/zstd/lib/compress/zstdmt_compress.h

## Purpose
Declares the internal multi-threaded compression interface used by Zstandard's compression frontend. The header intentionally warns that this is private API, no longer exported for direct application use, and requires `ZSTD_MULTITHREAD` support for context creation to succeed.

## Important APIs, Types, And Constants
The opaque type is `ZSTDMT_CCtx`. Construction and lifetime are handled by `ZSTDMT_createCCtx_advanced(unsigned nbWorkers, ZSTD_customMem cMem, ZSTD_threadPool *pool)`, `ZSTDMT_freeCCtx()`, and `ZSTDMT_sizeof_CCtx()`. Streaming is handled through `ZSTDMT_initCStream_internal()`, `ZSTDMT_compressStream_generic()`, and `ZSTDMT_nextInputSizeHint()`.

Constants bound the implementation: `ZSTDMT_NBWORKERS_MAX` defaults to 64 on 32-bit and 256 on wider targets, `ZSTDMT_JOBSIZE_MIN` defaults to 512 KB, `ZSTDMT_JOBLOG_MAX` is 29 or 30 depending on address width, and `ZSTDMT_JOBSIZE_MAX` is 512 MB or 1024 MB. These constants constrain allocation size, job splitting, and worker fan-out.

Progress and live tuning APIs include `ZSTDMT_toFlushNow()`, `ZSTDMT_updateCParams_whileCompressing()`, and `ZSTDMT_getFrameProgression()`. The init API accepts raw dictionaries, CDicts, content type, full `ZSTD_CCtx_params`, and pledged source size, while asserting at the contract level that callers must pass either a dict or a CDict, not both.

## Control Flow
Callers allocate a context, initialize a frame with `ZSTDMT_initCStream_internal()`, then repeatedly call `ZSTDMT_compressStream_generic()` with a `ZSTD_EndDirective`. The return value is the minimum data still needing flush, zero when fully flushed, or a zstd error code. During an active frame, callers may query immediate flushable bytes, update the subset of compression parameters compatible with the current frame, and inspect progress.

## State And Persistence
The header exposes no fields, so all state is encapsulated in the implementation. The comments document that reused contexts may retain prior allocations even when the next compression does not need them. A supplied `ZSTD_threadPool` is referenced by the MT context but not necessarily owned by it; a `ZSTD_customMem` allocator is threaded through context and pool allocations.

## Dependencies And Integration Points
It includes `zstd_deps.h` for `size_t`, defines `ZSTD_STATIC_LINKING_ONLY` to access advanced parameter types from `zstd.h`, and relies on `ZSTD_inBuffer`, `ZSTD_outBuffer`, `ZSTD_CCtx_params`, `ZSTD_customMem`, `ZSTD_threadPool`, `ZSTD_CDict`, and `ZSTD_frameProgression`. Its direct integration point is `ZSTD_compress.c`, which decides when to route compression through the MT backend.

## Risks And Edge Cases
Because this is private API, accidental external use can bind applications to unstable ABI. Compile-time overrides of worker and job-size limits can create unexpected memory profiles or violate assumptions in `zstdmt_compress.c` if set too aggressively. The dict-vs-CDict exclusivity and context-reuse comments are important caller obligations; violating them can lead to assertion failures or undefined behavior in internal builds.

## Test Signals
Build tests should cover configurations with and without `ZSTD_MULTITHREAD`, with custom limits, and with static linking consumers that include private headers. Runtime tests should verify context creation failure in non-MT builds, successful operation with owned and supplied thread pools in MT builds, and progress/flush hints during streaming.
