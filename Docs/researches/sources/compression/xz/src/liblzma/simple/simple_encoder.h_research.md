# sources/compression/xz/src/liblzma/simple/simple_encoder.h

## Purpose
Declares property size and encode helpers for simple/BCJ filters.

## Important APIs, Types, And Functions
- `lzma_simple_props_size()`.
- `lzma_simple_props_encode()`.

## Control Flow
No runtime flow.

## State And Persistence
No state.

## Dependencies And Integration Points
Includes `simple_coder.h`. Used by filter property encoding paths.

## Risks
Minimal; prototypes must match implementation and conditional build usage.

## Test Signals
Encoder property build and symmetry tests.
