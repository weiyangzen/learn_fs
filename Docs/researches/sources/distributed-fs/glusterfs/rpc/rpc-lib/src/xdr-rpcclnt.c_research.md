# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.c

## Purpose

`xdr-rpcclnt.c` implements client-side SunRPC XDR helpers: decode inbound RPC replies, encode outbound RPC calls, and serialize AUTH_UNIX credentials for requests. The file was read as a complete 104-line source.

## Important APIs, Types, and Functions

The exported functions are `xdr_to_rpc_reply`, `rpc_request_to_xdr`, and `auth_unix_cred_to_xdr`.

## Control Flow

`xdr_to_rpc_reply` validates input, clears `struct rpc_msg`, initializes accepted-reply verifier/result defaults, decodes with `xdr_replymsg`, and returns remaining program payload as an iovec. `rpc_request_to_xdr` validates the request and destination, encodes with `xdr_callmsg`, and returns the encoded byte range. `auth_unix_cred_to_xdr` is intended to convert `authunix_parms` into an iovec backed by caller-provided storage.

## State and Persistence Behavior

All state is transient and caller-owned. The helpers use stack `XDR` streams and write into caller-provided `struct rpc_msg`, iovec, or byte buffers.

## Dependencies and Integration Points

It uses RPC/XDR headers, `xdr-common.h` length/remainder macros, and Gluster validation/logging helpers. It is used by client/callback request paths and by `rpcsvc_callback_submit` through `rpc_request_to_xdr`.

## Risks and Edge Cases

`xdr_to_rpc_reply` accepts a `verfbytes` parameter but does not assign it to the decoded verifier storage, so verifier data persistence should be checked by callers. `auth_unix_cred_to_xdr` creates the XDR stream with `XDR_DECODE` despite its name and later reads `xdr_encoded_length`; this appears suspicious and should be verified with a credential serialization test. Reply decode depends on the result placeholder `xdr_void`, with application payload decoded separately from the remaining iovec.

## Test Signals

Tests should encode a call and decode it server-side, decode accepted and denied replies with trailing payload, verify reply accessor macros from `xdr-rpcclnt.h`, and specifically test `auth_unix_cred_to_xdr` against `xdr_authunix_parms` expected bytes to catch encode/decode direction errors.
