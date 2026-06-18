# File Research: sources/cow-pools/bcachefs-tools/raid/helper.c

## Purpose
Small helper routines for sorting RAID failure index vectors.

## APIs
- `raid_sort(int n, int *v)`
- `raid_insert(int n, int *v, int i)`

## Behavior
- `raid_sort()` uses fixed sorting networks for vectors of size 2 through 6.
- `raid_insert()` appends a value and swaps backward until sorted.
- Designed for very small vectors up to `RAID_PARITY_MAX`.

## Dependencies
Uses `internal.h` for compatibility macros and constants.
