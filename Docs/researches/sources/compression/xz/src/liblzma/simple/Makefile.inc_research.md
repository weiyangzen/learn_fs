# sources/compression/xz/src/liblzma/simple/Makefile.inc

## Purpose
Automake fragment that includes the common simple filter wrapper and conditionally includes encoder/decoder/property and architecture-specific BCJ filter sources.

## Important APIs, Types, And Functions
No C APIs. Build variables:
- Always adds `simple_coder.c`, `simple_coder.h`, and `simple_private.h`.
- `COND_ENCODER_SIMPLE` adds `simple_encoder.c/.h`.
- `COND_DECODER_SIMPLE` adds `simple_decoder.c/.h`.
- Per-filter conditions add `x86.c`, `powerpc.c`, `ia64.c`, `arm.c`, `armthumb.c`, `arm64.c`, `sparc.c`, and `riscv.c`.

## Control Flow
Build-time conditionals select feature-specific sources.

## State And Persistence
No runtime state.

## Dependencies And Integration Points
Included by liblzma build setup. Conditions must match configured filter support and public filter IDs.

## Risks
Mismatched conditions can expose filter IDs without implementations or compile unused code. Common wrapper must always be included when any simple filter is enabled.

## Test Signals
Autotools matrix builds for individual BCJ filters, encoder-only, decoder-only, and all-filters configurations.
