# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-rpcclnt.h

## Purpose

`xdr-rpcclnt.h` declares the client-side RPC XDR helper API and convenience macros for reading decoded RPC replies. The file was read as a complete 36-line header.

## Important APIs, Types, and Functions

It declares `xdr_to_rpc_reply`, `rpc_request_to_xdr`, and `auth_unix_cred_to_xdr`. Macros include `rpc_reply_xid`, `rpc_reply_status`, `rpc_accepted_reply_status`, and `rpc_reply_verf_flavour`.

## Control Flow

There is no executable flow. Client-side code builds `struct rpc_msg` calls, serializes them through `rpc_request_to_xdr`, decodes replies through `xdr_to_rpc_reply`, then uses the macros to inspect reply status and verifier flavor.

## State and Persistence Behavior

No state is owned by the header. It defines accessors over caller-owned `struct rpc_msg` values and declares functions using caller-owned buffers.

## Dependencies and Integration Points

It includes `arpa/inet.h`, `rpc/xdr.h`, `sys/uio.h`, `rpc/rpc_msg.h`, and `rpc/auth_unix.h`. The header is consumed by RPC client code and by server callback code in `rpcsvc.c`.

## Risks and Edge Cases

The macros depend on SunRPC `struct rpc_msg` layout and only cover accepted-reply verifier fields, so denied replies require direct struct handling. Any mismatch between this header and `xdr-rpcclnt.c` function behavior can affect client request serialization and callback RPCs.

## Test Signals

Compile coverage with the selected RPC/TIRPC library and round-trip tests for request encode/reply decode are the most useful signals. Denied reply tests should ensure callers do not use accepted-reply macros blindly.
