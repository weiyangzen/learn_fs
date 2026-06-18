# File Research: sources/block-storage/cryptsetup/lib/verity/rs.h

## Purpose
Declares Reed-Solomon codec structures and functions used by dm-verity FEC.

## Key Responsibilities
- Defines `data_t` byte symbols and the `struct rs` codec control block.
- Defines special zero index value `A0`.
- Provides `modnn()` field-index reduction helper.
- Declares RS context initialization/free plus 8-bit encode/decode functions.

## Important Details
- The structure stores Galois field lookup tables, generator polynomial, root count, primitive parameters, and shortened-block padding.
