# sources/distributed-fs/openafs/src/rx/xdr_refernce.c

## Purpose
`xdr_refernce.c` implements `xdr_reference`, the XDR helper for a non-null referenced object. The filename contains the historical misspelling `refernce`.

## Important APIs, Types, and Functions
- `xdr_reference(XDR *xdrs, caddr_t *pp, u_int size, xdrproc_t proc)` allocates storage for decode if needed, invokes the referenced object's XDR procedure, and frees storage on `XDR_FREE`.

## Control Flow
If `*pp` is `NULL`, decode allocates and zeroes `size` bytes, free returns success, and encode proceeds without allocation. The routine then calls `proc`; in free mode it frees the object and clears `*pp`.

## State and Persistence
Decoded referenced storage persists through `*pp` until an XDR_FREE pass. There is no module global state.

## Dependencies and Integration Points
Used by `xdr_pointer()` and generated XDR routines for recursive or indirect structures. Depends on caller-provided object XDR procedures and `osi_alloc`/`osi_free`.

## Risks and Edge Cases
Encode with `*pp == NULL` still calls the object procedure with a null pointer, so callers should use `xdr_pointer()` when nullability is part of the wire format. Partial decode failure can leave allocated storage that callers must free.

## Test Signals
Decode with null pointer should allocate and zero storage; free should clear it. A nested object procedure failure should propagate `FALSE`.
