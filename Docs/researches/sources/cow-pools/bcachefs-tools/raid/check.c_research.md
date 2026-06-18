# File Research: sources/cow-pools/bcachefs-tools/raid/check.c

## Purpose
RAID parity validation and failure scanning.

## Key APIs
- `raid_check()`
- `raid_scan()`

## Core Logic
- `raid_validate()` validates failed data blocks using extra valid parity blocks.
- Builds a coefficient matrix from `A(parity, disk)` values.
- Inverts the matrix with `raid_invert()`.
- Uses multiplication tables to reconstruct suspected data bytes.
- Verifies remaining parity equations reduce to zero.

## Behavior
- `raid_check()` accepts failed indexes across data and parity blocks, identifies valid parity indexes, and validates data failures.
- `raid_scan()` brute-forces combinations of possible failures and returns the first valid set size and indexes.
- Requires `size` to be a multiple of 64.
- Requires number of failed blocks for checking to be strictly less than parity count because an extra parity is needed for validation.

## Dependencies
Uses `internal.h`, `combo.h`, and `gf.h`.
