# sources/distributed-fs/openafs/src/rx/xdr_array.c

## Purpose
`xdr_array.c` implements generic counted variable-length array marshalling for user and kernel XDR callers.

## Important APIs, Types, and Functions
- `xdr_array(XDR *xdrs, caddr_t *addrp, u_int *sizep, u_int maxsize, u_int elsize, xdrproc_t elproc)` handles array count, optional allocation, per-element conversion, and freeing.

## Control Flow
The routine caps `maxsize` to avoid `c * elsize` overflow, marshals or reads the element count, validates count against maximum and preallocated capacity, allocates and zeroes storage on decode when `*addrp` is `NULL`, iterates each element through `elproc`, and frees allocated storage during `XDR_FREE`.

## State and Persistence
Decoded arrays may be allocated with `osi_alloc` and persist via `*addrp` until `XDR_FREE`. `*sizep` is updated to the decoded count.

## Dependencies and Integration Points
Used by rxgen-generated `xdr_*` routines for variable arrays. Relies on `xdr_u_int`, `osi_alloc`, `osi_free`, and caller-provided element XDR functions.

## Risks and Edge Cases
`elsize` must be nonzero; the overflow guard divides by `elsize`. Preallocated decode requires `*sizep` to represent capacity on entry. Element conversion failures can leave partially decoded arrays that the caller must clean up with `XDR_FREE`.

## Test Signals
Test zero-length arrays, max-size rejection, preallocated too-small rejection, allocation-on-decode, element failure propagation, and freeing resets `*addrp` to `NULL`.
