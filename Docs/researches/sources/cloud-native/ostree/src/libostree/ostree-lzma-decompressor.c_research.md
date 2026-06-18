# sources/cloud-native/ostree/src/libostree/ostree-lzma-decompressor.c

## Purpose
This file implements `OstreeLzmaDecompressor`, a `GConverter` wrapper around liblzma stream decoding.

## Important APIs and Control Flow
`_ostree_lzma_decompressor_new()` constructs the object. The instance owns an `lzma_stream` and an `initialized` flag. `reset` ends any active stream and restores `LZMA_STREAM_INIT`. `_ostree_lzma_decompressor_convert()` rejects non-empty input with zero output space, lazily initializes `lzma_stream_decoder()` with unlimited memory and no flags, sets input/output buffer pointers, runs `lzma_code(..., LZMA_RUN)`, records bytes consumed/produced for `LZMA_OK` and `LZMA_STREAM_END`, and delegates final result/error mapping to `_ostree_lzma_return()`.

## State, Dependencies, Integration, Risks, and Tests
State is per-object decompression progress. Dependencies are GObject, GIO, liblzma, and the common mapper. Integration points are OSTree object/archive decompression and any GLib converter stream that needs LZMA input. Risks include unlimited decoder memory, no explicit handling of `G_CONVERTER_INPUT_AT_END` flags, and partial-input semantics depending entirely on liblzma return codes. Tests should cover chunked decompression, stream end, reset/reuse, zero output buffer errors, corrupt input, and memory-limit expectations.
