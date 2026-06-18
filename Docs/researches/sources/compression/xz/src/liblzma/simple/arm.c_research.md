# sources/compression/xz/src/liblzma/simple/arm.c

## Purpose
Implements the ARM BCJ simple filter for 32-bit ARM branch-with-link instructions.

## Important APIs, Types, And Functions
- `arm_code()` converts 24-bit branch immediates between relative and absolute form.
- `arm_coder_init()` wires the filter through `lzma_simple_coder_init()`.
- Conditional exports `lzma_simple_arm_encoder_init()` and `lzma_simple_arm_decoder_init()`.

## Control Flow
The filter rounds size down to a 4-byte boundary, scans each instruction, and detects BL by `buffer[i+3] == 0xEB`. It reconstructs the 24-bit immediate, shifts by two, adds or subtracts `now_pos + i + 8` depending on encode/decode, shifts back, and writes the immediate bytes.

## State And Persistence
No filter-specific persistent state. Position comes from the wrapper's `now_pos`.

## Dependencies And Integration Points
Includes `simple_private.h`. Uses common simple wrapper with `unfiltered_max=4` and `alignment=4`.

## Risks
False positives in non-code data are possible. Correctness depends on 4-byte alignment and ARM PC bias of 8. It ignores incomplete trailing bytes by returning the filtered boundary.

## Test Signals
Encode/decode inverse tests for aligned ARM BL instructions, arbitrary-data bijection tests, start offset handling, and trailing 1-3 byte buffers.
