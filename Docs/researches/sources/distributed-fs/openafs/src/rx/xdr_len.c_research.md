# sources/distributed-fs/openafs/src/rx/xdr_len.c

## Purpose
`xdr_len.c` implements an XDR backend that measures the number of bytes an encode would produce without writing data.

## Important APIs, Types, and Functions
- `xdrlen_create(XDR *xdrs)` initializes an encode-only stream with `x_handy = 0`.
- `xdrlen_putint32()` and `xdrlen_putbytes()` increment `x_handy`.
- `xdrlen_getpos()` returns the accumulated length; `xdrlen_setpos()` sets it.

## Control Flow
Generic XDR encode routines call this backend as if writing to a stream. Integer and byte writes accumulate byte counts; reads and inline access return failure/NULL.

## State and Persistence
State is only `x_handy`, the current calculated encoded length. No buffers are allocated or persisted.

## Dependencies and Integration Points
Used by callers that need to size a memory buffer before a later `xdrmem_create` encode pass.

## Risks and Edge Cases
It does not enforce overflow on `x_handy`, which is an `int` in `XDR`. Decode operations are unsupported and should not be used. Length calculation depends on generic routines calling backend write operations for all bytes including padding.

## Test Signals
For a representative object, length from `xdrlen_create` should equal the final position after encoding the same object with `xdrmem_create`.
