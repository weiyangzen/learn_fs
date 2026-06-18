# sources/compression/xz/src/liblzma/rangecoder/Makefile.inc

## Purpose
Automake fragment that adds range-coder source/header files to liblzma builds depending on encoder/decoder feature conditions.

## Important APIs, Types, And Functions
No C APIs. Build variables used:
- `EXTRA_DIST` includes `rangecoder/price_tablegen.c`.
- `liblzma_la_SOURCES` always includes `range_common.h`.
- `COND_ENCODER_LZMA1` adds `range_encoder.h`, `price.h`, and `price_table.c`.
- `COND_DECODER_LZMA1` adds `range_decoder.h`.

## Control Flow
Build-time conditional inclusion controls which headers/tables are distributed and compiled into liblzma.

## State And Persistence
No runtime state. It persists build metadata in Automake variables.

## Dependencies And Integration Points
Included from the larger liblzma Automake setup. Coordinates with LZMA1 encoder/decoder feature toggles.

## Risks
Incorrect conditionals can omit headers or price table objects needed by encoder builds. `price_tablegen.c` must remain distributed even though generated table output is committed.

## Test Signals
Autotools builds with encoder-only, decoder-only, both, and minimal configurations should succeed. `make distcheck` should include the generator.
