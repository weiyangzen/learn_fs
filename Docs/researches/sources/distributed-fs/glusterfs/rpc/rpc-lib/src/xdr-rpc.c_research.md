# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.c

## Purpose

`xdr-rpc.c` implements server-side SunRPC XDR helpers: decode inbound RPC calls, construct empty/denied/accepted replies, encode replies, and decode AUTH_UNIX credential payloads. The file was read as a complete 198-line source.

## Important APIs, Types, and Functions

The exported functions are `xdr_to_rpc_call`, `rpc_fill_empty_reply`, `rpc_fill_denied_reply`, `rpc_fill_accepted_reply`, `rpc_reply_to_xdr`, and `xdr_to_auth_unix_cred`. `true_func` is a small XDR callback used as a successful reply result placeholder.

## Control Flow

`xdr_to_rpc_call` validates buffers, clears `struct rpc_msg`, points credential and verifier opaque-auth storage at caller-provided buffers or a local fallback, decodes with `xdr_callmsg`, and returns the remaining program payload as an iovec. Reply builders mutate a caller-owned `struct rpc_msg`: empty replies set xid/direction, denied replies fill mismatch/auth fields, accepted replies fill verifier and program-version mismatch or success result fields. `rpc_reply_to_xdr` encodes with `xdr_replymsg` and returns an iovec spanning the encoded bytes. `xdr_to_auth_unix_cred` prepares `authunix_parms` storage and decodes with `xdr_authunix_parms`.

## State and Persistence Behavior

All state is caller-provided and transient. The functions do not allocate persistent storage; credentials are decoded into caller-owned buffers and reply XDR is written into caller-owned memory.

## Dependencies and Integration Points

It uses libc/TIRPC RPC/XDR APIs, `xdr-common.h` stream-position macros, `xdr-rpc.h` declarations, and Gluster validation/logging helpers. It is used by `rpcsvc_request_create` and reply construction in `rpcsvc.c`, and by auth code that decodes AUTH_UNIX data.

## Risks and Edge Cases

If callers omit `credbytes` or `verfbytes`, both opaque auth bases can point at the same local fallback buffer during decode, which is only safe because decoded values are consumed before function return and callers that need persistence pass request-owned storage. Decode failures produce warning logs and `-1`, leaving callers responsible for sending correct RPC errors. Accepted-success replies use a placeholder `true_func` because the SunRPC interface expects a result encoder even when the program payload is sent separately.

## Test Signals

Tests should cover valid call decode with payload remainder, malformed call decode, denied replies for `RPC_MISMATCH` and `AUTH_ERROR`, accepted replies for `PROG_MISMATCH` and `SUCCESS`, reply encoding length, and AUTH_UNIX credential decoding with platform-specific gid pointer types.
