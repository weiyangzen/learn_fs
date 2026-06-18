# File Research: sources/cow-pools/bcachefs-tools/raid/intz.c

## Purpose
Portable integer C implementation of GENz triple parity.

## Key APIs
- `raid_genz_int32()`
- `raid_genz_int64()`

## Algorithm
GENz computes:
- P parity as XOR.
- Q parity by multiplying accumulated bytes by 2.
- R parity by dividing accumulated bytes by 2.

The functions process data blocks from last to first and operate on two 32-bit or two 64-bit chunks per loop iteration.

## Dependencies
Uses `internal.h` and `gf.h` for byte-lane GF arithmetic helpers.
