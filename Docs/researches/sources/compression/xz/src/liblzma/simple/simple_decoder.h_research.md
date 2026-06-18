# sources/compression/xz/src/liblzma/simple/simple_decoder.h

## Purpose
Declares property decoding for simple/BCJ filters.

## Important APIs, Types, And Functions
- `lzma_simple_props_decode()`.

## Control Flow
No runtime flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `simple_coder.h` so filter init prototypes and common types are visible to decoder property users.

## Risks
Minimal; declaration must stay in sync with implementation.

## Test Signals
Decoder build configurations and property decode tests.
