# File Research: sources/cow-pools/bcachefs-tools/raid/int.c

## Purpose
Portable integer C implementations of RAID parity generation and data recovery.

## Parity Generation
- `raid_gen1_int32()`, `raid_gen1_int64()`: RAID5 XOR parity.
- `raid_gen2_int32()`, `raid_gen2_int64()`: RAID6 P/Q parity using powers of 2.
- `raid_gen3_int8()` through `raid_gen6_int8()`: triple through six-way parity using Cauchy matrix coefficients.

## Recovery
- `raid_rec1_int8()`: recovers one data block using one chosen parity.
- `raid_rec2_int8()`: recovers two data blocks using two chosen parities.
- `raid_recX_int8()`: generic N-data-block recovery.
- Specialized fast paths are used for common parity choices:
  - `raid_rec1of1()` for RAID5 P parity.
  - `raid_rec2of2_int8()` for RAID6 P/Q recovery.

## Algorithm
- Constructs coefficient matrix from parity and data indexes.
- Inverts matrix over GF(2^8).
- Precomputes multiplication table pointers for inverse coefficients.
- Computes delta parity with `raid_delta_gen()`.
- Reconstructs missing bytes by multiplying delta parity vector by inverse matrix.

## Dependencies
Uses `internal.h` and `gf.h`; relies on field tables and generator matrix.
