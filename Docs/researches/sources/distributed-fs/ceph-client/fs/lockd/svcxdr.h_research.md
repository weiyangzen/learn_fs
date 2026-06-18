# sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/svcxdr.h` defines small inline XDR encode/decode helpers for basic NLM service data types shared by hand-written server XDR code. It handles status words, strings, cookies, and owner netobjs. The source was read as a complete 142-line file for this report.

## Important APIs, Types, and Functions

Inline functions are `svcxdr_decode_stats`, `svcxdr_encode_stats`, `svcxdr_decode_string`, `svcxdr_decode_cookie`, `svcxdr_encode_cookie`, `svcxdr_decode_owner`, and `svcxdr_encode_owner`. It relies on `NLM_MAXSTRLEN`, `NLM_MAXCOOKIELEN`, `XDR_MAX_NETOBJ`, `struct nlm_cookie`, and `struct xdr_netobj`.

## Control Flow

Each helper advances an `xdr_stream` by reading or reserving fixed or opaque fields. Decoders validate maximum lengths, obtain inline storage, and either copy into fixed lockd buffers or return pointers into the request buffer. Cookie decoding special-cases zero-length cookies by manufacturing a four-byte zero cookie for HPUX compatibility.

## State and Persistence Behavior

The helpers own no persistent state. String and owner decoders return pointers into the transient RPC receive buffer. Cookie decoding copies bytes into caller-provided `struct nlm_cookie` storage.

## Dependencies and Integration Points

This header is included by `xdr.c` and relies on SUNRPC `xdr_stream` helpers. The v1/v3 procedure tables use these helpers indirectly through `nlmsvc_decode_*` and `nlmsvc_encode_*` functions.

## Risks and Edge Cases

Length validation is the main safety boundary. Cookie length is intentionally limited to 32 bytes even though the protocol allows larger opaque cookies. Owner objects are limited by `XDR_MAX_NETOBJ`, while strings are limited by `NLM_MAXSTRLEN`. Returned request-buffer pointers must not outlive the RPC decode context.

## Test Signals

Fuzz XDR decode paths with oversized strings, cookies, and owner handles; validate zero-length cookie compatibility; test short/truncated streams; and run NLM v1/v3 lock procedures with binary owner handles and maximum-length caller strings.
