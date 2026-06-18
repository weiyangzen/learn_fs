# sources/compression/xz/src/liblzma/simple/powerpc.c

## Purpose
Implements BCJ filtering for big-endian PowerPC branch instructions.

## Important APIs, Types, And Functions
- `powerpc_code()` detects and converts PowerPC branch immediates.
- `powerpc_coder_init()` wires the wrapper.
- Conditional encoder/decoder init exports.

## Control Flow
The filter rounds size to 4 bytes, scans instructions, detects branch opcode `0x48`-class with link/absolute bit condition, reconstructs a 26-bit aligned source offset, adds/subtracts `now_pos + i`, and writes the destination bits while preserving low flag bits.

## State And Persistence
No filter-specific persistent state.

## Dependencies And Integration Points
Uses `simple_private.h` with wrapper `unfiltered_max=4`, `alignment=4`.

## Risks
Endian handling is manual. Detection choices affect false positives. Preserving low instruction bits is required for reversibility.

## Test Signals
Known PowerPC branch vectors, inverse encode/decode, random-data bijection, and trailing-byte handling.
