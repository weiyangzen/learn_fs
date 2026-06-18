# sources/distributed-fs/openafs/src/rx/xdr_update.c

## Purpose
`xdr_update.c` adds later Sun RPC helper routines needed by rpcgen/rxgen: nullable pointers and fixed-length vectors.

## Important APIs, Types, and Functions
- `xdr_pointer()` serializes a nullable pointer as a boolean presence flag followed by referenced object data.
- `xdr_vector()` serializes a fixed number of elements in static storage.

## Control Flow
`xdr_pointer()` computes `more_data` from `*objpp`, marshals it with `xdr_bool`, clears `*objpp` when absent, and otherwise delegates to `xdr_reference`. `xdr_vector()` loops `nelem` times and calls the element XDR routine for each fixed-size element.

## State and Persistence
Pointer decode can allocate storage via `xdr_reference`; vector handling does not allocate because storage is caller-owned.

## Dependencies and Integration Points
Used by generated XDR routines for recursive pointers and fixed arrays. Depends on `xdr_bool`, `xdr_reference`, and caller-provided element/object XDR functions.

## Risks and Edge Cases
During decode, the initial `more_data = (*objpp != NULL)` value is overwritten by the wire boolean, so callers must rely on output state after success. Recursive data structures can allocate deeply and need a later XDR_FREE traversal.

## Test Signals
Round-trip null and non-null pointers, ensure absent pointers decode to `NULL`, and verify fixed-vector element counts and failure propagation.
