# sources/compression/xz/src/liblzma/lzma/lzma_decoder.h

## Purpose
Declares the internal LZMA decoder interface used by raw filter initialization, LZMA2, `.lzma`/lzip-style property parsing, and memory accounting.

## Important APIs, Types, And Functions
- `lzma_lzma_decoder_init()` initializes an LZMA decoder in a filter chain.
- `lzma_lzma_decoder_memusage()` and `_nocheck()` report memory requirements, with `_nocheck()` intended for callers that already validated lc/lp/pb or do not need them yet.
- `lzma_lzma_props_decode()` decodes 5-byte LZMA properties into `lzma_options_lzma`.
- `lzma_lzma_lclppb_decode()` decodes the compact lc/lp/pb property byte.
- When `LZMA_LZ_DECODER_H` is visible, `lzma_lzma_decoder_create()` allocates and configures only the LZ-level raw decoder callbacks.

## Control Flow
The header itself has no runtime flow. It gates `lzma_lzma_decoder_create()` behind the LZ decoder include guard so only lower-level LZ integration code sees the raw create helper.

## State And Persistence
No state is stored in this header. It forward-declares functions that allocate and manipulate `lzma_lzma1_decoder` state defined privately in `lzma_decoder.c`.

## Dependencies And Integration Points
Includes `common.h` for liblzma base types. It is consumed by LZMA1/LZMA2 decoder setup code and property decoders for container formats.

## Risks
The `_nocheck` memory-usage API relies on caller-side validation; misuse can report memory for invalid option structures. The conditional declaration pattern can hide APIs from translation units unless include order is correct.

## Test Signals
Compile coverage should ensure both public and `LZMA_LZ_DECODER_H` declaration modes work. ABI/API tests should verify property decode and memory-usage entry points remain available under decoder builds.
