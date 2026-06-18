# File Research: sources/cow-pools/bcachefs-tools/raid/gf.h

## Purpose
Inline Galois-field helper operations for RAID parity math.

## APIs / Macros
- `mul()`, `inv()`, `pow2()`, `table()`, `A()`
- `v_8()`, `v_32()`, `v_64()`
- `x2_32()`, `x2_64()`
- `d2_32()`, `d2_64()`

## Behavior
- Field multiplication, inverse, exponent, and generator coefficients are table-driven.
- `x2_*` multiplies each byte lane by 2 in GF(2^8).
- `d2_*` divides each byte lane by 2 in GF(2^8).
- Uses `BUG_ON()` for invalid inverse/exponent input.

## Dependencies
Relies on tables declared in `internal.h`: `gfmul`, `gfinv`, `gfexp`, and `gfgen`.
