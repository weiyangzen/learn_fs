# sources/compression/lz4/lib/lz4file.h

## Purpose
`lz4file.h` declares the static file wrapper API implemented by `lz4file.c`. It gives callers a compact `FILE*`-based interface for LZ4 frame decompression and compression while hiding the underlying frame contexts and temporary buffers.

## Important APIs And Types
The header includes `<stdio.h>` for `FILE*` and `lz4frame_static.h` for frame types, static export macros, and static-only helpers. It forward declares opaque handle types `LZ4_readFile_t` and `LZ4_writeFile_t`.

The read API is `LZ4F_readOpen(LZ4_readFile_t** lz4fRead, FILE* fp)`, `LZ4F_read(LZ4_readFile_t* lz4fRead, void* buf, size_t size)`, and `LZ4F_readClose(LZ4_readFile_t* lz4fRead)`. The write API is `LZ4F_writeOpen(LZ4_writeFile_t** lz4fWrite, FILE* fp, const LZ4F_preferences_t* prefsPtr)`, `LZ4F_write(LZ4_writeFile_t* lz4fWrite, const void* buf, size_t size)`, and `LZ4F_writeClose(LZ4_writeFile_t* lz4fWrite)`.

All declarations use `LZ4FLIB_STATIC_API`, signaling that this API is intended for static-linking or explicitly published static symbols rather than the default shared-library surface.

## Control Flow And Contract
Callers open a binary `FILE*` themselves, then call `LZ4F_readOpen()` or `LZ4F_writeOpen()` to allocate a wrapper handle. Reads and writes are performed through the wrapper, and the wrapper handle must be closed with the matching close function. The comments specify that output handle arguments are out parameters whose initial values are ignored and valid only on success.

The header documents that `LZ4F_read()` returns bytes read into the caller buffer and `LZ4F_write()` returns bytes written from the caller buffer. Error returns are frame error codes and should be checked with `LZ4F_isError()`.

## State And Persistence
The header deliberately hides state layout. Runtime state lives in the opaque handle implementation: frame context, buffers, sticky write error state, and the caller's `FILE*`. The underlying `FILE*` is not documented as being closed by the wrapper, and implementation confirms that only wrapper resources are freed.

## Dependencies And Integration Points
This is a convenience layer on top of `lz4frame.h`/`lz4frame_static.h`, not a replacement for the full streaming frame API. It integrates with standard C file I/O and inherits frame preferences from `LZ4F_preferences_t` on write. Because it includes `lz4frame_static.h`, it also defines `LZ4F_STATIC_LINKING_ONLY` before including `lz4frame.h`.

## Risks And Edge Cases
The API name prefix overlaps the core frame API (`LZ4F_*`) while being static-only and file-specific, so link visibility and documentation need care. The comments contain a duplicated "LZ4 File Decompression" heading above the write API, which can confuse generated docs but not compilation. Since binary-mode `FILE*` is required, Windows callers must avoid text mode. Error values share the unsigned `size_t`/`LZ4F_errorCode_t` convention, so callers that compare directly to negative values will mishandle failures.

## Test Signals
Header-level checks should compile both C and C++ consumers, verify static-only symbol visibility under default and `LZ4F_PUBLISH_STATIC_FUNCTIONS` builds, confirm binary `FILE*` read/write examples round-trip with `LZ4F_isError()` checks, and ensure consumers can pass custom `LZ4F_preferences_t` through `LZ4F_writeOpen()`.
