# sources/compression/zstd/lib/legacy/zstd_legacy.h

## Purpose
`zstd_legacy.h` is the internal dispatch layer for decoding pre-1.0 zstd frame formats. It detects legacy frame magic numbers, reports decompressed sizes and frame sizes where supported, performs one-shot legacy decompression, and manages streaming decompression contexts for supported legacy versions.

## Important APIs, Types, And Functions
- `ZSTD_LEGACY_SUPPORT` defaults to `8` when undefined or zero, which means no legacy version headers are included. Lower values include support down to that version.
- `ZSTD_isLegacy()` reads the first four bytes and returns a supported legacy version number 1..7 or `0`.
- `ZSTD_getDecompressedSize_legacy()` returns frame content size for versions 5..7 when their headers expose it, otherwise `0`.
- `ZSTD_decompressLegacy()` dispatches one-shot decompression to version-specific `ZSTDv0X_decompress` or `ZSTDv0X_decompress_usingDict()` implementations.
- `ZSTD_findFrameSizeInfoLegacy()` dispatches frame-size discovery and fills a `ZSTD_frameSizeInfo`, including `nbBlocks` when a decompressed bound is known.
- `ZSTD_findFrameCompressedSizeLegacy()` returns only the compressed-size component.
- `ZSTD_freeLegacyStreamContext()`, `ZSTD_initLegacyStream()`, and `ZSTD_decompressLegacyStream()` manage streaming decode contexts for versions 4..7.

## Control Flow
Compile-time `#if (ZSTD_LEGACY_SUPPORT <= N)` blocks include the version headers and compile the matching switch cases. Detection starts with `MEM_readLE32()` of the frame magic. One-shot decompression normalizes `NULL` zero-size pointers to a local dummy byte to avoid passing null into legacy decoders, then switches on detected version. Versions 1..4 use older no-dictionary APIs where available; versions 5..7 allocate a version-specific DCtx, decompress with optional dictionary, then free it.

Frame-size helpers dispatch to version-specific find functions and convert an oversized compressed-frame report into `ERROR(srcSize_wrong)`. Streaming initialization frees a previous context if the version changes, creates or reuses the version-specific ZBUFF DCtx, initializes it with the dictionary, and stores it through `legacyContext`. Streaming decompression advances `ZSTD_inBuffer.pos` and `ZSTD_outBuffer.pos` according to bytes consumed/produced by the version-specific continue call.

## State And Persistence
This is a header-only collection of `MEM_STATIC` functions. Persistent state exists only in caller-owned `legacyContext` pointers for streaming decompression. The implementation may allocate version-specific contexts in init and frees them through `ZSTD_freeLegacyStreamContext()`. One-shot version 5..7 decompression allocates and frees a temporary DCtx inside the call.

## Dependencies And Integration Points
It includes zstd common memory, private error helpers, and internal buffer/frame types. Depending on `ZSTD_LEGACY_SUPPORT`, it includes `zstd_v01.h` through `zstd_v07.h`. It integrates with the main decoder path to identify unsupported modern-vs-legacy frames, find frame sizes, and delegate decompression to archived decoders.

## Risks And Edge Cases
- The meaning of `ZSTD_LEGACY_SUPPORT` is inverted by threshold: `<= 5` includes v5 support, while the default `8` includes none.
- Versions 1..3 do not support streaming through this layer and return `ERROR(version_unsupported)` for stream operations.
- `ZSTD_getDecompressedSize_legacy()` returns `0` both for unknown size and for unsupported/non-legacy formats, so callers need additional detection when ambiguity matters.
- Header-only static functions increase compile-time coupling to legacy version headers and internal zstd types.
- Dummy-byte substitution for `NULL` zero-size buffers avoids legacy null handling issues but relies on assertions for consistency.
- If a legacy frame-size function returns a compressed size larger than available input, this layer rewrites it to `srcSize_wrong`.

## Test Signals
Tests should compile with multiple `ZSTD_LEGACY_SUPPORT` values, detect each supported magic number, reject unsupported versions, decompress known v1..v7 frames where enabled, validate dictionary paths for v5..v7, exercise streaming v4..v7 with chunked input/output, and check frame-size behavior for truncated inputs.
