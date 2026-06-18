# sources/distributed-fs/openafs/src/rx/xdr_mem.c

## Purpose
`xdr_mem.c` implements an XDR backend over a caller-provided memory buffer.

## Important APIs, Types, and Functions
- `xdrmem_create()` initializes the stream with buffer base, current pointer, size, and operation.
- `xdrmem_getint32()`/`xdrmem_putint32()` read/write network-order 32-bit units.
- `xdrmem_getbytes()`/`xdrmem_putbytes()` copy raw bytes.
- `xdrmem_getpos()`/`xdrmem_setpos()` support buffer-relative seeking.
- `xdrmem_inline()` returns a direct pointer to contiguous buffer space when available.

## Control Flow
Every read/write verifies `x_handy` has enough remaining bytes, updates remaining capacity, copies or converts data, and advances `x_private`. `setpos` recomputes remaining capacity relative to the original buffer and current end.

## State and Persistence
The backend persists no ownership; it mutates the caller-provided buffer and stores cursor/capacity state in the `XDR` handle. `destroy` is a no-op.

## Dependencies and Integration Points
This is the primary backend for unit tests and in-memory encode/decode of rxgen data structures.

## Risks and Edge Cases
The code casts buffer pointers to `afs_int32 *`, so alignment matters. `x_handy` is capped at `INT_MAX`, limiting very large buffers. `setpos` compares against the current original end, not a separately stored total length.

## Test Signals
Round-trip primitives and composites, verify failures on short buffers, verify `getpos`/`setpos`, and confirm inline access advances position.
