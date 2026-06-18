# File Research: sources/block-storage/cryptsetup/lib/verity/rs_decode_char.c

## Purpose
Implements byte-symbol Reed-Solomon decoding and correction based on libfec.

## Key Responsibilities
- Computes syndromes for the received RS block.
- Returns immediately when all syndromes are zero.
- Uses Berlekamp-Massey to compute the error locator polynomial.
- Uses Chien search to find error roots/locations.
- Computes the error evaluator polynomial.
- Applies corrections to the data block.
- Returns the number of corrected symbols or `-1` for uncorrectable errors.

## Important Details
- Rejects configurations with `nroots >= 256` due to fixed stack buffers.
- Location correction skips positions inside shortened padding.
- The function mutates the input data buffer in place.
- It expects an initialized `struct rs` with lookup tables from `init_rs_char()`.

## Dependencies
Uses `rs.h` and standard memory helpers.
