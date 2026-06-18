# sources/compression/xz/src/liblzma/lzma/lzma_encoder.h

## Purpose
Declares internal and semi-public LZMA encoder entry points for filter-chain setup, property encoding, memory usage, and LZMA2 raw encoder reuse.

## Important APIs, Types, And Functions
- Forward declaration `lzma_lzma1_encoder`.
- `lzma_lzma_encoder_init()` initializes an LZMA encoder filter.
- `lzma_lzma_encoder_memusage()` reports required memory.
- `lzma_lzma_props_encode()` emits 5-byte LZMA properties.
- `lzma_lzma_lclppb_encode()` encodes lc/lp/pb to one byte.
- Under `LZMA_LZ_ENCODER_H`, raw helpers `lzma_lzma_encoder_create()`, `lzma_lzma_encoder_reset()`, and `lzma_lzma_encode()` are visible for LZMA2.

## Control Flow
No runtime flow is defined. Conditional declarations separate public internal filter APIs from lower-level raw LZ encoder integration.

## State And Persistence
The header hides the concrete encoder struct, enforcing state access through private implementation and raw helper functions.

## Dependencies And Integration Points
Includes `common.h`. Consumed by `lzma_encoder_private.h`, LZMA2 encoder code, and filter initialization tables.

## Risks
Compile-time visibility depends on include order and feature macros. Callers of raw helpers must satisfy LZ-layer contracts around match finder state, output limits, and reset sequencing.

## Test Signals
Build configurations with encoder-only, LZMA2, and property support should all compile. Property encode and raw LZMA2 chunk encoding tests exercise these declarations.
