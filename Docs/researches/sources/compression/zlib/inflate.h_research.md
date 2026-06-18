# sources/compression/zlib/inflate.h

## Purpose
`inflate.h` defines the private state model and mode enumeration for zlib decompression.

## Important APIs, Types, and Functions
It conditionally enables gzip support with `GUNZIP`, defines `inflate_mode` values such as `HEAD`, `TYPE`, `TABLE`, `LEN`, `MATCH`, `CHECK`, `DONE`, `BAD`, and `SYNC`, and defines `struct inflate_state`. The state includes wrapper flags, checksum counters, gzip header pointer, sliding window metadata, bit accumulator, dynamic Huffman work arrays, decode table storage, distance sanity flag, and progress markers.

## Control Flow, State, and Persistence
The header documents the inflate state transitions from wrapper headers through block decoding and trailer validation. Runtime persistence is entirely in `struct inflate_state`, which survives across `inflate()` calls until reset or `inflateEnd()`.

## Dependencies and Integration Points
It depends on `code` and `ENOUGH` from `inftrees.h` and zlib stream types from internal/public headers. `inflate.c`, `infback.c`, and `inffast.c` all consume this exact layout.

## Risks and Test Signals
Risks include mode-order assumptions in `inflateStateCheck()`, table-size coupling to `inftrees.h`, and accidental external use despite private warnings. Compile coverage plus streaming tests that suspend/resume in many modes are the key signals.
