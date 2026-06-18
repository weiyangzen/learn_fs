# sources/compression/zstd/lib/deprecated/zbuff_decompress.c

## Purpose
`zbuff_decompress.c` implements deprecated ZBUFF decompression APIs as compatibility wrappers around the modern `ZSTD_DStream` streaming decompression API.

## Important APIs, Types, And Functions
Context wrappers are `ZBUFF_createDCtx()`, `ZBUFF_createDCtx_advanced()`, and `ZBUFF_freeDCtx()`. Initialization wrappers are `ZBUFF_decompressInit()` and `ZBUFF_decompressInitDictionary()`. The streaming wrapper is `ZBUFF_decompressContinue()`. Buffer-size helpers are `ZBUFF_recommendedDInSize()` and `ZBUFF_recommendedDOutSize()`.

## Control Flow
Creation/free forward directly to `ZSTD_createDStream*` and `ZSTD_freeDStream()`. Initialization forwards to `ZSTD_initDStream()` or `ZSTD_initDStream_usingDict()`. `ZBUFF_decompressContinue()` adapts legacy pointer/count arguments to `ZSTD_outBuffer` and `ZSTD_inBuffer`, calls `ZSTD_decompressStream()`, then writes output position and input position back to `*dstCapacityPtr` and `*srcSizePtr`.

## State And Persistence
The underlying `ZSTD_DStream` owns all stream state: frame parsing stage, loaded dictionary, input buffering, output buffering, history window, checksum state, and progress. The wrapper layer stores no independent state. Dictionaries loaded by initialization persist according to the modern DStream semantics.

## Dependencies And Integration Points
The file includes `../zstd.h` with deprecation warnings disabled for `ZSTD_initDStream_usingDict`, defines `ZBUFF_STATIC_LINKING_ONLY`, and includes `zbuff.h`. It is the decompression half of the legacy buffered API and interoperates with modern zstd frames.

## Risks
The wrapper must preserve legacy consumed/produced byte reporting even when the modern stream returns a hint or asks for output flushing. Tiny buffers, pending buffered output, and partial input consumption are the main behavioral compatibility risks. Dictionary lifetime and error propagation are delegated to the modern API but remain visible through legacy names.

## Test Signals
Useful tests include streaming decompression with one-byte input/output chunks, dictionary-compressed frames, multiple frames, skippable frames, checksum failures, return-value hints across partial calls, and recommended sizes matching `ZSTD_DStreamInSize()`/`ZSTD_DStreamOutSize()`.
