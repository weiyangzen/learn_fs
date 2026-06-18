# sources/compression/zstd/lib/deprecated/zbuff_compress.c

## Purpose
`zbuff_compress.c` implements deprecated ZBUFF compression APIs as compatibility wrappers around the modern `ZSTD_CStream`/`ZSTD_CCtx` streaming compression API.

## Important APIs, Types, And Functions
Context wrappers are `ZBUFF_createCCtx()`, `ZBUFF_createCCtx_advanced()`, and `ZBUFF_freeCCtx()`. Initialization wrappers are `ZBUFF_compressInit()`, `ZBUFF_compressInitDictionary()`, and `ZBUFF_compressInit_advanced()`. Streaming wrappers are `ZBUFF_compressContinue()`, `ZBUFF_compressFlush()`, and `ZBUFF_compressEnd()`. Buffer-size helpers are `ZBUFF_recommendedCInSize()` and `ZBUFF_recommendedCOutSize()`.

## Control Flow
Creation and free forward directly to `ZSTD_createCStream*` and `ZSTD_freeCStream()`. Basic init forwards to `ZSTD_initCStream()`. Dictionary init resets the session, sets compression level, loads the dictionary, and returns zero on success. Advanced init preserves historical `pledgedSrcSize == 0` as unknown, resets the session, sets pledged size, validates and applies compression parameters, applies frame parameters, loads the dictionary, and returns zero. Continue/flush/end wrappers construct `ZSTD_outBuffer` and `ZSTD_inBuffer` shims, call the corresponding ZSTD stream function, then write consumed/produced byte counts back through legacy pointer arguments.

## State And Persistence
All state lives in the underlying `ZSTD_CStream`. Initialization changes session parameters, pledged size, frame flags, and loaded dictionary state. Continue/flush/end mutate stream progress and buffered output through the ZSTD API. The wrapper file stores no global or static mutable state.

## Dependencies And Integration Points
It defines `ZBUFF_STATIC_LINKING_ONLY`, includes `zbuff.h`, and uses `error_private.h` for `FORWARD_IF_ERROR`. It bridges old applications to current compression APIs and must remain consistent with the typedef that makes `ZBUFF_CCtx` a `ZSTD_CStream`.

## Risks
Pointer out-parameters must always be updated to the actual consumed/produced counts, including partial-progress cases. Advanced init must keep old pledged-size semantics and correctly map deprecated `ZSTD_parameters` fields to modern individual parameters. Because wrappers forward errors directly, callers must continue using `ZBUFF_isError()`/`ZSTD_isError()` on returned `size_t` values.

## Test Signals
Round-trip tests through `ZBUFF_compressContinue()` plus modern decompression are the key signal. Additional coverage should include tiny output buffers, repeated flush calls, end-stream completion, dictionary init, advanced init with `pledgedSrcSize == 0`, invalid compression parameters, custom allocators, and recommended sizes matching `ZSTD_CStreamInSize()`/`ZSTD_CStreamOutSize()`.
