# File Research: sources/cow-pools/bcachefs-tools/raid/combo.h

## Purpose
Inline helpers for enumerating permutations and combinations.

## APIs
- `permutation_first()`
- `permutation_next()`
- `combination_first()`
- `combination_next()`

## Behavior
- Permutations are with repetition, equivalent to nested loops over `0..n`.
- Combinations are without repetition and return indexes in increasing order.
- `*_next()` returns `0` when enumeration is complete.
- Uses assertions to enforce `0 < r <= n`.

## Usage
Used by RAID scanning/checking paths to test possible failed block sets.
