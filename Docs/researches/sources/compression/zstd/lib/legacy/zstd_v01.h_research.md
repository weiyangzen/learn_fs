# sources/compression/zstd/lib/legacy/zstd_v01.h

Purpose: public legacy header for decoding Zstandard v0.1.x frames. It exposes the one-shot, frame-size, error-test, context, and streaming APIs implemented in `zstd_v01.c`, plus the v0.1 magic constants used by the legacy dispatcher.

Important APIs/types/functions: declares `ZSTDv01_decompress()`, `ZSTDv01_findFrameSizeInfoLegacy()`, `ZSTDv01_isError()`, opaque `ZSTDv01_Dctx`, `ZSTDv01_createDCtx()`, `ZSTDv01_freeDCtx()`, `ZSTDv01_decompressDCtx()`, `ZSTDv01_resetDCtx()`, `ZSTDv01_nextSrcSizeToDecompress()`, and `ZSTDv01_decompressContinue()`. It defines `ZSTDv01_magicNumber` as `0xFD2FB51E` for the v0.1 big-endian stream value and `ZSTDv01_magicNumberLE` as `0x1EB52FFD` for little-endian detection by `zstd_legacy.h`.

Control flow: consumers either call `ZSTDv01_decompress()` with the exact compressed frame size and a destination capacity at least as large as the expected decompressed size, or create/reset a `ZSTDv01_Dctx` and alternate `ZSTDv01_nextSrcSizeToDecompress()` with `ZSTDv01_decompressContinue()`. The streaming contract reports zero-byte progress for headers and positive sizes for decoded block payloads. `ZSTDv01_findFrameSizeInfoLegacy()` scans a frame and returns the compressed byte count plus a decompressed upper bound through output parameters.

State and persistence: the header intentionally keeps `ZSTDv01_Dctx` opaque. Context allocation, reset, and free are owned by the caller, but all internal decode state is hidden in `zstd_v01.c`. The API carries no dictionary parameter and exposes no stable serialized state. The frame-size helper assumes non-NULL `cSize` and `dBound` pointers.

Dependencies and integration points: includes only `<stddef.h>` for `size_t` and uses `extern "C"` guards for C++ consumers. It is conditionally included by `zstd_legacy.h` when the build enables support down to v0.1. That dispatcher uses the magic macros for version detection, the one-shot function for legacy decompression, and the frame-size helper for legacy frame probing.

Risks: the comments contain copy/paste references to `ZSTDv01_isError()` in places that matter for v0.1 but mirror other legacy headers; callers still must use the matching `ZSTDv01_isError()` declared here. The API requires exact compressed sizes and caller-allocated output capacity, so misuse tends to surface as generic error codes rather than partial decompression. Streaming misuse is easy if callers ignore the exact requested source size or assume decoded output is produced for every call.

Test signals: compile/link tests should verify C and C++ inclusion, opaque context lifecycle, one-shot decode, streaming decode parity with one-shot decode, magic-number routing through `ZSTD_isLegacy()`, and frame-size helper behavior on valid, truncated, and wrong-prefix inputs.
