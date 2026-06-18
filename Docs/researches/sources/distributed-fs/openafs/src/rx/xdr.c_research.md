# sources/distributed-fs/openafs/src/rx/xdr.c

## Purpose
`xdr.c` implements generic Sun RPC XDR primitives for OpenAFS RX: scalar integers/chars/bools/enums, opaque byte sequences, counted bytes, discriminated unions, strings, wrapping/free helpers, and allocator hooks.

## Important APIs, Types, and Functions
- Scalar routines: `xdr_int`, `xdr_u_int`, `xdr_long`, `xdr_u_long`, `xdr_char`, `xdr_u_char`, `xdr_short`, `xdr_u_short`, `xdr_bool`, `xdr_enum`, and `xdr_afs_time64`.
- Buffer routines: `xdr_opaque`, `xdr_bytes`, and `xdr_string`.
- Higher-level routines: `xdr_union`, `xdr_wrapstring`, `xdrfree_string`, `xdr_alloc`, and `xdr_free`.
- Uses the `XDR` ops table from `xdr.h` for stream-specific reads/writes.

## Control Flow
Most routines switch on `xdrs->x_op`. Encode writes canonical 32-bit network-order units through `XDR_PUTINT32`/`XDR_PUTBYTES`; decode reads through `XDR_GETINT32`/`XDR_GETBYTES`; free releases allocations created by decode. Composite routines first marshal lengths/discriminants, validate maxima, then dispatch to element or arm routines.

## State and Persistence
No module-level mutable state. Allocation and deallocation go through `osi_alloc`/`osi_free`, so decoded objects persist until an XDR_FREE pass or explicit helper frees them.

## Dependencies and Integration Points
This is the generic type layer used by rxgen-generated code and by hand-written RX tests. It depends on `xdr.h` macros and concrete stream implementations such as memory, RX call, stdio, record, and length-counting XDR.

## Risks and Edge Cases
The file contains notable safety checks: preallocated `xdr_bytes` decode refuses sizes larger than caller-provided capacity; `xdr_string` refuses preallocated decode buffers, caps huge `maxsize`, rejects embedded NUL bytes, and poisons failed strings so later free size is calculable. Scalar casts can truncate platform `long`/`int` values to XDR's 32-bit representation. `xdr_union` relies on a sentinel `NULL_xdrproc_t` in the choices table.

## Test Signals
Round-trip encode/decode tests over `xdrmem_create` are direct signals for scalars, strings, bytes, and unions. Fuzz/negative tests should assert rejection for oversized byte counts, embedded-NUL strings, and too-small preallocated byte arrays.
