# sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h

## Purpose

`sources/distributed-fs/glusterfs/rpc/xdr/src/xdr-generic.h` declares GlusterFS's generic XDR/iovec helper API and portability macros for invoking `xdrproc_t`. The source was read as a complete 76-line file for this report.

## Important APIs, Types, and Functions

The header defines XDR stream length macros, `XDR_BYTES_PER_UNIT`, the platform-specific `PROC` macro, and prototypes for `xdr_serialize_generic`, `xdr_to_generic`, `xdr_to_generic_payload`, `xdr_bytes_round_up`, `xdr_length_round_up`, and `xdr_vector_round_up`.

## Control Flow

There is no runtime flow here. The compile-time `PROC` macro chooses whether to call an XDR procedure as `proc(xdr, res)` on NetBSD or `proc(xdr, res, 0)` elsewhere to accommodate platform typedef differences.

## State and Persistence Behavior

No state is owned. The declared helpers operate on caller-owned buffers and structures.

## Dependencies and Integration Points

It depends on `sys/uio.h`, `rpc/types.h`, `rpc/xdr.h`, and `glusterfs/compat.h`. It is the common include for XDR wrapper files and generated-protocol adapters.

## Risks and Edge Cases

The macros inspect XDR implementation fields directly, which can break if the system XDR layout changes. The `PROC` portability shim must match each platform's `xdrproc_t` signature. Duplicate length macros also appear in `glusterfs3.h`, so changes should stay consistent.

## Test Signals

Cross-platform compile coverage on Linux, NetBSD, FreeBSD, and macOS is important. Wrapper tests that include this header and call generated XDR functions through `PROC` validate the signature abstraction.
