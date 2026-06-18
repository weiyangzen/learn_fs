# sources/compression/zstd/lib/legacy/zstd_v02.h

Purpose: public legacy header for decoding Zstandard v0.2.x frames. It presents the same API shape as the v0.1 header while naming the v0.2-specific entry points and exposing the v0.2 magic number used by legacy format detection.

Important APIs/types/functions: declares `ZSTDv02_decompress()`, `ZSTDv02_findFrameSizeInfoLegacy()`, `ZSTDv02_isError()`, opaque `ZSTDv02_Dctx`, `ZSTDv02_createDCtx()`, `ZSTDv02_freeDCtx()`, `ZSTDv02_decompressDCtx()`, `ZSTDv02_resetDCtx()`, `ZSTDv02_nextSrcSizeToDecompress()`, and `ZSTDv02_decompressContinue()`. It defines `ZSTDv02_magicNumber` as `0xFD2FB522`.

Control flow: callers can use one-shot decompression by providing an exact compressed size and a preallocated destination, or use the streaming API by creating/resetting a context and alternating source-size queries with continuation calls. Header and block-header calls can return zero decoded bytes by design. Frame-size probing is exposed through output parameters, returning the consumed compressed size and a conservative decompressed bound.

State and persistence: `ZSTDv02_Dctx` is opaque and allocated/freed through the header’s lifecycle functions. Internal state includes history tracking and literal buffering, but the header exposes only the streaming pull contract. No dictionary argument or persisted state handle is available. `ZSTDv02_findFrameSizeInfoLegacy()` assumes non-NULL result pointers.

Dependencies and integration points: includes `<stddef.h>` and wraps declarations in `extern "C"` for C++ compatibility. `zstd_legacy.h` includes it when support down to v0.2 is enabled, uses the magic constant to return legacy version 2, dispatches decompression to `ZSTDv02_decompress()`, and uses the frame-size helper during legacy frame scanning.

Risks: documentation comments contain copy/paste references to testing failures with `ZSTDv01_isError()` even though this header declares `ZSTDv02_isError()`. Consumers should use the version-matched error predicate. As with v0.1, the API depends on exact source chunk sizes in streaming mode and sufficient destination capacity in both streaming and one-shot modes. The declared `ZSTDv02_decompressDCtx()` is part of the advanced surface, so ABI users can bind to the context-based path directly.

Test signals: compile/link coverage should include C and C++ consumers, one-shot decompression, context lifecycle, direct context decompression, streaming decompression, frame-size helper routing, and magic-number detection through the legacy dispatcher. Header-level regression tests should catch accidental prototype drift because the legacy dispatcher relies on these names under `ZSTD_LEGACY_SUPPORT <= 2`.
