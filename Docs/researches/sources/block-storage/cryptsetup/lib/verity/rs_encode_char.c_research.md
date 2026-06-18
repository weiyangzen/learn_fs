# File Research: sources/block-storage/cryptsetup/lib/verity/rs_encode_char.c

## Purpose
Initializes and frees Reed-Solomon contexts and encodes byte-symbol parity.

## Key Responsibilities
- Validates RS parameter ranges.
- Allocates and populates Galois field log/antilog tables.
- Verifies that the generator polynomial is primitive.
- Builds the RS generator polynomial from configured roots.
- Encodes data into parity bytes through feedback shift-register logic.
- Frees all RS lookup/generator allocations.

## Important Details
- Supports up to 8-bit symbols for `data_t`.
- `pad` implements shortened RS blocks.
- Generator polynomial is converted to index form for faster encoding.
- Encoding writes parity into caller-provided storage and does not allocate.

## Dependencies
Uses `rs.h` and standard allocation/memory functions.
