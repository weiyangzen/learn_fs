# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpc.h

## Purpose

`xdr-rpc.h` declares the server-side RPC XDR helper API and Gluster-specific RPC auth flavor numbers. It also provides macros for reading fields from `struct rpc_msg` calls and printf-format helpers for RPC identifiers. The file was read as a complete 93-line header.

## Important APIs, Types, and Functions

It defines `gf_rpc_authtype_t` with `AUTH_GLUSTERFS`, `AUTH_GLUSTERFS_v2`, and `AUTH_GLUSTERFS_v3`. It declares `xdr_to_rpc_call`, `rpc_fill_empty_reply`, `rpc_fill_denied_reply`, `rpc_fill_accepted_reply`, `rpc_reply_to_xdr`, and `xdr_to_auth_unix_cred`. Accessor macros include `rpc_call_xid`, `rpc_call_direction`, `rpc_call_rpcvers`, `rpc_call_program`, `rpc_call_progver`, `rpc_call_progproc`, and credential/verifier flavor/length helpers.

## Control Flow

There is no executable flow in the header. It defines how server code decodes inbound calls, builds replies, and reads RPC identifiers without spreading SunRPC union-field details throughout the codebase.

## State and Persistence Behavior

No state is owned here. The macros read caller-owned `struct rpc_msg` instances, and declared functions operate on caller-owned buffers and iovecs.

## Dependencies and Integration Points

The header includes platform-specific RPC headers, `arpa/inet.h`, `rpc/xdr.h`, and `sys/uio.h`. It is consumed by `rpcsvc.c`, `xdr-rpc.c`, auth code, and logging paths that need format-width compatibility for RPC ids on Darwin or systems without `<rpc/rpc.h>`.

## Risks and Edge Cases

The macros depend on SunRPC/TIRPC `struct rpc_msg` union layout. The auth flavor values use RFC5531 unused ranges; changing them would break wire compatibility. Format macros differ by platform, so incorrect use can produce warnings or bad log output for xid/program fields.

## Test Signals

Compile coverage across Linux, Darwin, Solaris, and no-`rpc/rpc.h` configurations is the main signal. Wire tests should verify GlusterFS auth flavor numbers and field accessor macros against decoded RPC calls.
