# sources/compression/zstd/lib/decompress/zstd_ddict.h

## Purpose
Declares the decompression-side internal helpers for `ZSTD_DDict`. The public constructor/destructor/sizing APIs are declared in `zstd.h`; this header adds the private accessors and DCtx-copy helper needed by decompression internals.

## Important APIs And Types
The header includes `zstd_deps.h` for `size_t` and `zstd.h` for `ZSTD_DDict`, `ZSTD_DCtx`, and public DDict prototypes. It declares `ZSTD_DDict_dictContent(const ZSTD_DDict*)`, `ZSTD_DDict_dictSize(const ZSTD_DDict*)`, and `ZSTD_copyDDictParameters(ZSTD_DCtx*, const ZSTD_DDict*)`.

The comments enumerate the public functions already declared elsewhere: `ZSTD_createDDict()`, `ZSTD_createDDict_byReference()`, `ZSTD_createDDict_advanced()`, `ZSTD_freeDDict()`, `ZSTD_initStaticDDict()`, `ZSTD_sizeof_DDict()`, `ZSTD_estimateDDictSize()`, and `ZSTD_getDictID_fromDict()`.

## Control Flow
There is no executable control flow in the header. Callers include it when they need to inspect dictionary byte ranges or install DDict-derived state into a decompression context before decoding.

## State And Persistence
No state is defined here. The functions operate on opaque `ZSTD_DDict` and `ZSTD_DCtx` objects whose fields are defined in decompression implementation headers and `zstd_ddict.c`.

## Dependencies And Integration Points
This header is the boundary between the DDict implementation and decompression code that should not know the full `struct ZSTD_DDict_s` layout. It integrates with `zstd_decompress.c` and related internal decompression paths that need dictionary content, size, entropy tables, and prefix/window parameters.

## Risks And Edge Cases
The helpers assume non-null arguments in the implementation. Since they are internal, callers are expected to validate object lifetimes and not use DDict pointers after free. Adding fields to `ZSTD_DDict` does not require changing this header, but changing these helper contracts affects all decompression dictionary users.

## Test Signals
Compile coverage should ensure internal decompression users can include the header without exposing private struct layout. Runtime coverage comes from DDict decompression tests that exercise helper calls through dictionary-based decompression, including by-copy, by-reference, raw-content, and full-dictionary modes.
