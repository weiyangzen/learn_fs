# sources/compression/xz/src/liblzma/rangecoder/range_decoder.h

## Purpose
Defines the range decoder state and a macro library for safe/resumable and fast LZMA bit decoding, with optional branchless C and x86-64 inline assembly variants.

## Important APIs, Types, And Functions
- `LZMA_RANGE_DECODER_CONFIG` selects optimized variants.
- `RC_BIT_MODEL_OFFSET` supports branchless probability updates.
- `lzma_range_decoder` stores `range`, `code`, and initialization bytes left.
- `rc_read_init()`, `rc_to_local()`, `rc_from_local()`, `rc_reset()`, and `rc_is_finished()`.
- Core macros: `rc_normalize[_safe]`, `rc_if_0[_safe]`, `rc_update_0`, `rc_update_1`, `rc_bit[_safe]`, `rc_bittree3/6/8`, `rc_bittree_rev4`, `rc_bit_add_if_1`, `rc_matched_literal`, and `rc_direct[_safe]`.

## Control Flow
The decoder initializes by reading five bytes, requiring the first to be zero. Fast macros assume the caller has guaranteed enough input and directly advance `rc_in_ptr`. Safe macros check input exhaustion and jump to `out` after saving the caller-provided sequence. Optional branchless C macro replacements remove some branches for selected operations. On x86-64 GCC/Clang builds, the default config selects inline assembly for normal bit trees, reverse bit trees, variable reverse bits, matched literals, and direct bits.

## State And Persistence
The persistent state is `lzma_range_decoder`, but performance macros copy it and input position into locals with `rc_to_local()` and store them back with `rc_from_local()`. Probability arrays are mutated by the update macros at each decoded bit.

## Dependencies And Integration Points
Includes `range_common.h`. Used heavily by `lzma_decoder.c`, whose local variable names and labels are part of the macro contract. Optimized variants depend on compiler, architecture, and `LZMA_RANGE_DECODER_CONFIG`.

## Risks
This header is macro-heavy and relies on caller variables such as `rc`, `rc_bound`, `rc_in_ptr`, `symbol`, `coder`, and `out`. Safe macros use `goto out`, making integration fragile. Inline assembly has portability and compiler-constraint risk. Fast macros require sufficient input; wrong `LZMA_IN_REQUIRED` assumptions can overread. Probability update math must remain bit-exact with encoder.

## Test Signals
Decoder round trips under default, `HAVE_SMALL`, branchless C, and disabled-assembly configurations. One-byte input fuzzing exercises safe macros. Cross-compiler and non-x86 builds are important. Corrupt stream tests should verify first-byte and `rc_is_finished()` checks.
