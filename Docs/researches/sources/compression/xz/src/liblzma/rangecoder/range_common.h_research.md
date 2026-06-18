# sources/compression/xz/src/liblzma/rangecoder/range_common.h

## Purpose
Defines common constants, reset macros, and the `probability` type shared by range encoder and decoder implementations.

## Important APIs, Types, And Functions
- Constants: `RC_SHIFT_BITS`, `RC_TOP_BITS`, `RC_TOP_VALUE`, `RC_BIT_MODEL_TOTAL_BITS`, `RC_BIT_MODEL_TOTAL`, and `RC_MOVE_BITS`.
- Macros: `bit_reset(prob)` and `bittree_reset(probs, bit_levels)`.
- `typedef uint16_t probability`.

## Control Flow
Only reset macros perform loops/assignments at call sites. `bittree_reset` iterates through all modeled tree nodes.

## State And Persistence
No stored state. Defines the representation for adaptive probability arrays used across encoder and decoder structs.

## Dependencies And Integration Points
Includes `common.h` unless `BUILDING_PRICE_TABLEGEN` is defined. Used by `range_encoder.h`, `range_decoder.h`, `price.h`, and LZMA model structs.

## Risks
Changing probability width or range constants affects ABI-internal memory layout, performance, generated price tables, and inline assembly assumptions. Comments note 2024 branchless C/x86-64 assembly assumes `uint16_t`.

## Test Signals
Full encoder/decoder round trips, generated price table comparison, x86-64 assembly builds, and memory-usage regression tests.
