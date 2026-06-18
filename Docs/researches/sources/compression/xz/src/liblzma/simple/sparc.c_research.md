# sources/compression/xz/src/liblzma/simple/sparc.c

## Purpose
Implements BCJ filtering for SPARC branch/call-like instructions.

## Important APIs, Types, And Functions
- `sparc_code()` detects SPARC branch encodings and converts addresses.
- `sparc_coder_init()` wires wrapper settings.
- Conditional encoder/decoder init exports.

## Control Flow
The filter rounds size to 4 bytes and scans words. It detects instructions whose first bytes match SPARC call/branch patterns, builds a big-endian 32-bit source, shifts by two, adds/subtracts `now_pos + i`, shifts back, reconstructs sign/format bits, and writes the word.

## State And Persistence
No filter-specific state.

## Dependencies And Integration Points
Uses `simple_private.h` with `unfiltered_max=4`, `alignment=4`.

## Risks
Manual sign and bit reconstruction is delicate. False positives in non-code data can hurt compression. Only full aligned words are transformed.

## Test Signals
Known SPARC vectors, encode/decode inverse tests, random-data bijection, and trailing-byte tests.
