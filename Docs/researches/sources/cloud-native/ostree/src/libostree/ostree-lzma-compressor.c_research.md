# sources/cloud-native/ostree/src/libostree/ostree-lzma-compressor.c

## Purpose
This file implements `OstreeLzmaCompressor`, a `GConverter` that compresses data using liblzma. It is a GObject wrapper around `lzma_stream` for use in GLib converter streams.

## Important APIs and Control Flow
The type stores optional construct-only `params`, an `lzma_stream`, and an `initialized` flag. `_ostree_lzma_compressor_new(params)` constructs it. The converter `reset` method calls `lzma_end()`, restores `LZMA_STREAM_INIT`, and clears initialization. `_ostree_lzma_compressor_convert()` rejects non-empty input with zero output space, lazily initializes `lzma_easy_encoder()` at preset 8 with `LZMA_CHECK_CRC64`, wires input/output buffers into the stream, maps GLib flags to `LZMA_RUN`, `LZMA_SYNC_FLUSH`, or `LZMA_FINISH`, then calls `lzma_code()`. Bytes read/written are computed from remaining stream availability, and results flow through `_ostree_lzma_return()`.

## State, Dependencies, Integration, Risks, and Tests
State is per-object stream state plus the unused/stored params variant. Dependencies are GObject, GIO converter interfaces, liblzma, and the common mapper. Integration points are archive/object compression paths that need streaming XZ/LZMA output. Risks include hard-coded compression level/check despite the `params` property, incomplete handling of no-progress buffer conditions, and correct finalization after partial conversions. Tests should cover streaming chunks, flush, finish, reset/reuse, small output buffers, and corrupt/unsupported initialization errors.
