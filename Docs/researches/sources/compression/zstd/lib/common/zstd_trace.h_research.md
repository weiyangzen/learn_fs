# sources/compression/zstd/lib/common/zstd_trace.h

## Purpose
`zstd_trace.h` defines the optional weak-symbol tracing ABI for compression and decompression calls. It lets external instrumentation observe begin/end events without adding hard runtime dependencies when tracing is unavailable.

## Important APIs, Types, and Functions
The key type is `ZSTD_Trace`, carrying version, streaming flag, dictionary ID, dictionary coldness, dictionary size, uncompressed size, compressed size, resolved compression parameters, and the active compression/decompression context pointer. `ZSTD_TraceCtx` is an opaque nonzero token returned by begin hooks. Optional weak hook declarations are `ZSTD_trace_compress_begin()`, `ZSTD_trace_compress_end()`, `ZSTD_trace_decompress_begin()`, and `ZSTD_trace_decompress_end()`.

## Control Flow, State, and Persistence
The header owns no state. Preprocessor checks set `ZSTD_HAVE_WEAK_SYMBOLS` only for conservative GNU/ELF architecture and OS combinations, excluding Apple, Windows, MinGW, Cygwin, and AIX. `ZSTD_TRACE` defaults to weak-symbol availability unless explicitly overridden. When tracing is disabled, the hook declarations and trace structs are not compiled.

## Dependencies and Integration Points
It includes `<stddef.h>` and forward declares zstd context/parameter structs. `zstd_internal.h` includes it unless `ZSTD_NO_TRACE` is defined; compression/decompression implementations can call begin/end hooks guarded by `ZSTD_TRACE`. External profilers or observability libraries can define the weak symbols to receive events.

## Risks and Test Signals
The ABI is intentionally version-sensitive: `version` must remain the first field so consumers can reject unknown layouts. Weak-symbol support is platform-sensitive, so build tests should cover enabled and disabled tracing targets. Runtime tests can define hooks, ensure begin nonzero tokens are passed to matching end calls, and verify tracing compiles out cleanly under `ZSTD_NO_TRACE`.
