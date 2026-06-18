# sources/distributed-fs/openafs/src/rx/xdr_afsuuid.c

## Purpose
`xdr_afsuuid.c` provides the XDR routine for the built-in `afsUUID` type.

## Important APIs, Types, and Functions
- `xdr_afsUUID(XDR *xdrs, afsUUID *objp)` serializes fields in UUID order: `time_low`, `time_mid`, `time_hi_and_version`, two clock sequence bytes, and six node bytes.

## Control Flow
The function is a straight-line sequence of primitive XDR calls. It returns `FALSE` on the first failed field conversion and `TRUE` only after the node vector succeeds.

## State and Persistence
No local persistent state. For `XDR_FREE`, behavior delegates to primitive routines and `xdr_vector`; no dynamic UUID storage is allocated here.

## Dependencies and Integration Points
Depends on `xdr_afs_uint32`, `xdr_u_short`, `xdr_char`, and `xdr_vector`. Used wherever OpenAFS RPC interfaces expose `afsUUID`.

## Risks and Edge Cases
The cast to `xdrproc_t` for `xdr_char` reflects the legacy function pointer signature mismatch. A field-order change would break wire compatibility.

## Test Signals
Round-trip an `afsUUID` through memory XDR and compare every field. Negative stream tests should fail when any primitive field read/write is truncated.
