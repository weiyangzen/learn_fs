# sources/distributed-fs/openafs/src/rx/xdr_stdio.c

## Purpose
`xdr_stdio.c` implements an XDR backend over a standard `FILE *` stream.

## Important APIs, Types, and Functions
- `xdrstdio_create()` initializes the backend.
- `xdrstdio_getint32()`/`xdrstdio_putint32()` use `fread`/`fwrite` with network-order conversion except on `mc68000`.
- `xdrstdio_getbytes()`/`xdrstdio_putbytes()` transfer raw bytes.
- `xdrstdio_getpos()`/`xdrstdio_setpos()` use `ftell`/`fseek`.
- `xdrstdio_destroy()` flushes the file; it does not close it.

## Control Flow
Each backend operation directly invokes stdio and returns `FALSE` if the expected item count is not transferred. Inline access is unsupported and returns `NULL`.

## State and Persistence
The `XDR` handle borrows the `FILE *`. The file content is persistent according to the caller's stream; this backend only flushes on destroy.

## Dependencies and Integration Points
Useful for file-based XDR serialization and legacy Sun RPC compatibility paths. Generic XDR routines use this through the ops vector.

## Risks and Edge Cases
The function uses old K&R declarations, which can hide prototype issues. It does not close the stream. `fread(addr, len, 1)` reports failure unless the whole byte block is read.

## Test Signals
Encode to a temporary file, rewind, decode, and compare values. Test `getpos`/`setpos` and flush behavior after destroy.
