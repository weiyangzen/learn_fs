# sources/compression/xz/src/liblzma/lzma/lzma_encoder_private.h

## Purpose
Defines private LZMA encoder data structures, constants, helper macros, and optimum-parser prototypes shared by encoder implementation files.

## Important APIs, Types, And Functions
- `not_equal_16()` compares the first two candidate bytes using unaligned reads when available.
- `OPTS` defines the optimal parser window size as 4096 entries.
- `lzma_length_encoder` stores length probabilities plus price tables and counters.
- `lzma_optimal` stores one node in the optimal parse graph.
- `struct lzma_lzma1_encoder_s` contains range encoder, size/out-limit state, LZMA state/reps, match candidates, mode flags, adaptive probabilities, price tables, and optimum arrays.
- Prototypes declare `lzma_lzma_optimum_fast()` and `lzma_lzma_optimum_normal()`.

## Control Flow
The header has no direct control flow but its structs define the state layout used by the encoder loop and parser functions.

## State And Persistence
All persistent LZMA encoder state is defined here. It spans compression progress (`uncomp_size`), output-limit behavior, adaptive probabilities, match finder lookahead caches, and normal parser graph state.

## Dependencies And Integration Points
Includes `lz_encoder.h`, `range_encoder.h`, `lzma_common.h`, and `lzma_encoder.h`. It is the private bridge between the main encoder, fast optimum parser, and normal optimum parser.

## Risks
Struct layout changes affect memory usage and all encoder code. `not_equal_16()` depends on safe buffer availability for two bytes. `OPTS` must remain consistent with `LOOP_INPUT_MAX` in `lzma_encoder.c`. Price arrays are large and tied to LZMA constants.

## Test Signals
Compile and round-trip all encoder modes after any change. Memory-usage tests should track `sizeof(lzma_lzma1_encoder)`. Parser boundary tests should cover `OPTS` sizing.
