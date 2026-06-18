# sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h

## Purpose

`sources/distributed-fs/ceph-client/fs/nfsd/nfs4xdr_gen.h` declares the generated XDR helper interface used by NFSD NFSv4 XDR code. It exposes encode/decode prototypes for a small set of generated NFSv4.1 and extension types while hiding the generated helper implementation in `nfs4xdr_gen.c`. The source was read as a complete 35-line generated header.

## Important APIs, Types, and Functions

The header includes Linux integer types, SUNRPC XDR stream declarations, xdrgen definitions/builtins, and generated `linux/sunrpc/xdrgen/nfs4_1.h` type declarations. It declares bool-returning encode/decode helpers for `fattr4_open_arguments`, `fattr4_time_deleg_access`, `fattr4_time_deleg_modify`, `aclmodel4`, `aclscope4`, `posixacetag4`, and `posixaceperm4`.

All functions take a `struct xdr_stream *` plus either a mutable destination pointer for decode or a value/const pointer for encode. The enum/value helpers use typed generated aliases such as `aclmodel4`, `aclscope4`, `posixacetag4`, and `posixaceperm4`.

## Control Flow

The header has no executable control flow. Compile-time include guards prevent duplicate declarations, and consumers call into `nfs4xdr_gen.c` for the actual stream manipulation and validation.

## State and Persistence Behavior

The header defines no state and performs no persistence. It is part of the build-time ABI between generated XDR helper implementation and handwritten NFSD XDR code.

## Dependencies and Integration Points

The primary handwritten integration point is `nfs4xdr.c`, which includes this header to use generated helpers for POSIX ACL extension values, delegated timestamp attributes, ACL trueform/scope values, and OPEN_ARGUMENTS capability encoding. The header is generated from `Documentation/sunrpc/xdr/nfs4_1.x`; manual modifications are explicitly marked as non-durable.

## Risks and Edge Cases

Prototype drift between this header, `nfs4xdr_gen.c`, generated `nfs4_1.h` types, and handwritten `nfs4xdr.c` would cause compile failures or subtle ABI mismatches. Because all helpers return `bool`, callers must map failures to protocol errors consistently, usually `nfserr_bad_xdr` for decode and `nfserr_resource` for encode.

## Test Signals

Compile coverage is the primary signal for declaration compatibility. Integration tests that exercise POSIX ACL extension attributes, delegated timestamp setattrs, and OPEN_ARGUMENTS fattr encoding verify that the generated declarations remain aligned with both generated implementation and handwritten call sites.
