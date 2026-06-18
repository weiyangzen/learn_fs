# sources/distributed-fs/openafs/src/rx/xdr_prototypes.h

## Purpose
`xdr_prototypes.h` declares OpenAFS XDR functions after `XDR` and related types are defined by `xdr.h`.

## Important APIs, Types, and Functions
It declares UUID, int32, int64, RX-call backend creation, generic XDR primitives, array/reference/pointer/vector helpers, memory and length backends, record-stream APIs, and allocation hooks.

## Control Flow
No runtime control flow.

## State and Persistence
No runtime state. The `XDR_AFS_DECLS_ONLY` guard allows a reduced declaration set for contexts needing only AFS-specific declarations.

## Dependencies and Integration Points
Included at the end of `xdr.h`; forward-declares `struct rx_call` for `xdrrx_create`. Keeps generated and hand-written code from relying on implicit declarations.

## Risks and Edge Cases
Prototype mismatch with implementation files would surface as ABI/calling bugs, especially around `xdrproc_t` casts and platform-specific declarations. It declares `osi_alloc`/`osi_free` fallbacks when macros are absent.

## Test Signals
Compile with strict prototypes across user/kernel targets and generated rxgen output. Link tests should catch missing implementations.
