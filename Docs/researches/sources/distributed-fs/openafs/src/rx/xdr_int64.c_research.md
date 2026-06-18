# sources/distributed-fs/openafs/src/rx/xdr_int64.c

## Purpose
`xdr_int64.c` implements signed and unsigned 64-bit integer XDR routines for OpenAFS.

## Important APIs, Types, and Functions
- `xdr_int64()` delegates to `xdr_afs_int64()`.
- `xdr_afs_int64()` marshals high signed 32 bits followed by low unsigned 32 bits.
- `xdr_uint64()` delegates to `xdr_afs_uint64()`.
- `xdr_afs_uint64()` marshals high and low unsigned 32-bit halves.

## Control Flow
Decode reads high then low words and reconstructs by shifting high left 32 and adding low. Encode splits the local 64-bit value into high and low words and writes both. Free succeeds without action.

## State and Persistence
No allocation or persistent state.

## Dependencies and Integration Points
Used by `xdr_afs_time64()` and any rxgen interface using 64-bit OpenAFS integer types. Depends on backend 32-bit XDR ops.

## Risks and Edge Cases
Signed right-shift behavior and reconstruction must preserve negative values on supported compilers. The low mask uses `0xFFFFFFFFL`, whose width depends on platform `long`, though cast targets are fixed OpenAFS types.

## Test Signals
Round-trip `0`, `1`, `-1`, signed min/max, and values crossing the 32-bit boundary. Wire-order tests should confirm high word precedes low word.
