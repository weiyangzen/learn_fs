# sources/compression/xz/src/liblzma/simple/armthumb.c

## Purpose
Implements BCJ filtering for ARM-Thumb BL instruction pairs.

## Important APIs, Types, And Functions
- `armthumb_code()` converts two-halfword Thumb branch immediates.
- `armthumb_coder_init()` wires the simple wrapper.
- Conditional exports `lzma_simple_armthumb_encoder_init()` and decoder init.

## Control Flow
If fewer than four bytes are available it filters nothing. Otherwise it scans every two bytes through `size - 4`, detects the high-halfword/low-halfword BL pattern, reconstructs the immediate, converts with `now_pos + i + 4` on encode or subtracts on decode, writes updated halfwords, and skips the second half of the matched instruction.

## State And Persistence
No filter-specific state. `now_pos` is maintained by the wrapper.

## Dependencies And Integration Points
Uses `simple_private.h` and wrapper parameters `unfiltered_max=4`, `alignment=2`.

## Risks
Detection may match non-code data. Offsets depend on Thumb PC bias of 4 and halfword alignment. The loop leaves trailing bytes for the wrapper when an incomplete instruction remains.

## Test Signals
Encode/decode inverse tests for Thumb BL, unaligned start-offset rejection through wrapper, trailing byte behavior, and random-data bijection checks.
