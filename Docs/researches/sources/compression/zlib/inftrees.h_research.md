# sources/compression/zlib/inftrees.h

## Purpose
`inftrees.h` declares the private Huffman decode-table representation and table-building functions used by zlib inflate internals.

## Important APIs, Types, and Functions
It defines the `code` struct with `op`, `bits`, and `val`, the operation-value encoding, `ENOUGH_LENS`, `ENOUGH_DISTS`, `ENOUGH`, `codetype` values `CODES`, `LENS`, and `DISTS`, plus declarations for `inflate_table()` and `inflate_fixed()`.

## Control Flow, State, and Persistence
The header has no runtime flow. Its constants define the maximum persistent table storage embedded in `struct inflate_state`, and its operation encoding drives the decode loops in `inflate.c`, `infback.c`, and `inffast.c`.

## Dependencies and Integration Points
It is included by all inflate implementation files. The comments explicitly tie `ENOUGH_*` to the root-bit choices used in `inflate_table()` calls, so changes require recalculation with `examples/enough.c`.

## Risks and Test Signals
Risks include changing table root sizes without updating `ENOUGH_*`, misinterpreting `op` bits, and exposing private internals to applications. Compile-time size checks are absent, so runtime table-building coverage and dynamic-block fuzzing are important signals.
