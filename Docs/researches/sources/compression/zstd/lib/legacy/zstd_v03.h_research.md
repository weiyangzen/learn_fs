# Research: sources/compression/zstd/lib/legacy/zstd_v03.h

Purpose: Declares the public compatibility API for zstd v0.3 frame decompression. It is the include used by the legacy dispatcher when `ZSTD_LEGACY_SUPPORT <= 3`.

Important APIs and types: The simple API is `ZSTDv03_decompress(dst, maxOriginalSize, src, compressedSize)`. Frame sizing is exposed through `ZSTDv03_findFrameSizeInfoLegacy(src, srcSize, cSize, dBound)`, which reports compressed frame length and an upper decompressed bound. Error probing is `ZSTDv03_isError(size_t code)`. Advanced/direct streaming declarations use the opaque `ZSTDv03_Dctx` with `ZSTDv03_createDCtx()`, `ZSTDv03_freeDCtx()`, `ZSTDv03_decompressDCtx()`, `ZSTDv03_resetDCtx()`, `ZSTDv03_nextSrcSizeToDecompress()`, and `ZSTDv03_decompressContinue()`. `ZSTDv03_magicNumber` is the version-detection constant `0xFD2FB523`.

Control flow and integration: Callers either provide an entire v0.3 frame to `ZSTDv03_decompress()` or drive the direct streaming state machine by repeatedly asking for the next exact input size and passing that amount to `ZSTDv03_decompressContinue()`. `zstd_legacy.h` includes this header conditionally, detects the magic number, dispatches one-shot decompression to `ZSTDv03_decompress()`, and dispatches frame-size queries to `ZSTDv03_findFrameSizeInfoLegacy()`.

State and persistence behavior: The header exposes an opaque context, so callers do not own internal tables or history buffers directly. A context can be reused after `ZSTDv03_resetDCtx()`. Streaming callers are responsible for retaining output history in the layout expected by the implementation when matches refer to previous blocks.

Dependencies and integration points: Only includes `<stddef.h>` and is C++ compatible through `extern "C"`. The actual error-code values come from the implementation's shared legacy error scheme. It is part of the legacy decoder family selected by `ZSTD_LEGACY_SUPPORT`.

Risks: The comment for error checking references `ZSTDv01_isError()` even though the declared checker is `ZSTDv03_isError()`. `ZSTDv03_decompressDCtx()` takes `void* ctx`, making the type contract weaker than the opaque context declarations around it, and the corresponding public wrapper is not present in `zstd_v03.c`. The API cannot report an exact decompressed content size for v0.3 frames, only the implementation's upper-bound estimate.

Test signals: Compile C and C++ includers, verify the magic number in `ZSTD_isLegacy()`, check one-shot and context-based decompression paths on known v0.3 samples, verify `findFrameSizeInfoLegacy()` outputs on valid/truncated frames, and ensure version 3 is rejected by the generic legacy streaming wrapper while the direct `ZSTDv03_*Continue()` API still works.
