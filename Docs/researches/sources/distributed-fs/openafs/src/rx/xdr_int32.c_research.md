# sources/distributed-fs/openafs/src/rx/xdr_int32.c

## Purpose
`xdr_int32.c` provides OpenAFS-specific 32-bit signed and unsigned integer XDR routines.

## Important APIs, Types, and Functions
- `xdr_afs_int32()` directly gets/puts an `afs_int32`.
- `xdr_afs_uint32()` directly gets/puts an `afs_uint32` through casts to the 32-bit backend API.

## Control Flow
Each routine checks `x_op`: decode calls `XDR_GETINT32`, encode calls `XDR_PUTINT32`, free returns `TRUE`, and unknown operations return `FALSE`.

## State and Persistence
No persistent state and no allocation.

## Dependencies and Integration Points
These routines are foundational for rxgen-generated code and other XDR primitives, including UUID and 64-bit values.

## Risks and Edge Cases
Unsigned support relies on casting to `afs_int32 *` for the backend. Correctness depends on backend network-byte-order conversion and OpenAFS integer type widths.

## Test Signals
Round-trip boundary values: `0`, `-1`, `INT32_MIN`, `INT32_MAX`, and `UINT32_MAX`.
