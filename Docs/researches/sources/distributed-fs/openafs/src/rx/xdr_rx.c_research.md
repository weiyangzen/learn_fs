# sources/distributed-fs/openafs/src/rx/xdr_rx.c

## Purpose
`xdr_rx.c` implements an XDR backend over an RX call stream.

## Important APIs, Types, and Functions
- `xdrrx_create(XDR *xdrs, struct rx_call *call, enum xdr_op op)` binds an XDR handle to an RX call.
- `xdrrx_getint32()`/`xdrrx_putint32()` use `rx_Read32`/`rx_Write32` and network-order conversion.
- `xdrrx_getbytes()`/`xdrrx_putbytes()` use `rx_Read`/`rx_Write`.
- `xdrrx_inline()` intentionally returns `NULL`.

## Control Flow
Generic XDR routines dispatch to RX reads and writes. Each operation returns success only when RX reads/writes exactly the requested byte count. AIX kernel builds pin stack pages around RX calls to avoid paging under network interrupt constraints.

## State and Persistence
The `XDR` handle stores only a borrowed `struct rx_call *` in `x_private`; it does not own or destroy the call.

## Dependencies and Integration Points
This is the backend used by rxgen client/server stubs and hand-written RX tests such as `kctest.c`/`kstest.c`.

## Risks and Edge Cases
Position operations are not supported and are set to `NULL`. Exact-length RX read/write semantics mean partial stream errors fail the XDR operation. The AIX stack-pinning path tracks failures but continues.

## Test Signals
Client/server RPC round trips through rxgen stubs and direct `xdrrx_create` tests. Short read/write simulation should force `FALSE`.
