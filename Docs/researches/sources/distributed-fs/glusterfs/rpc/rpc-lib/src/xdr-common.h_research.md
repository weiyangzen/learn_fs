# sources/distributed-fs/glusterfs/rpc/rpc-lib/src/xdr-common.h

## Purpose

`xdr-common.h` provides shared XDR/RPC constants, compatibility macros, dump-program identifiers, and helper macros for measuring encoded/decoded XDR stream positions. The file was read as a complete 115-line header.

## Important APIs, Types, and Functions

It defines `enum gf_dump_procnum`, `GLUSTER_DUMP_PROGRAM`, `GLUSTER_DUMP_VERSION`, `GF_MAX_AUTH_BYTES`, `GF_AUTH_GLUSTERFS_MAX_GROUPS`, `GF_AUTH_GLUSTERFS_MAX_LKOWNER`, and platform compatibility aliases for XDR integer function names. It also exposes `xdr_decoded_remaining_addr`, `xdr_decoded_remaining_len`, `xdr_encoded_length`, and `xdr_decoded_length` macros.

## Control Flow

There is no runtime control flow. Consumers create an `XDR` stream, call an XDR encode/decode function, then use these macros to locate the remaining payload or determine how many bytes were encoded.

## State and Persistence Behavior

No state is owned here. The macros inspect mutable fields inside a caller-owned `XDR` object, especially `x_private`, `x_handy`, and `x_base`.

## Dependencies and Integration Points

It includes RPC auth/types headers and `sys/uio.h`, with NetBSD, Linux, Darwin, and Solaris compatibility sections. It is used by server and client XDR helpers (`xdr-rpc.c`, `xdr-rpcclnt.c`) and by the built-in dump RPC program in `rpcsvc.c`.

## Risks and Edge Cases

The auth-size macros encode the on-wire limit assumptions for GlusterFS auth v2/v3; incorrect lock-owner or group lengths can exceed `MAX_AUTH_BYTES`. The XDR position macros depend on libc/TIRPC `XDR` internals, so portability changes in XDR implementation layout are risky. Platform alias macros must stay consistent with the RPC library selected by configure.

## Test Signals

Tests should decode a call/reply with trailing payload and verify remaining address/length; encode a reply and verify encoded length; and exercise auth-size boundary calculations for AUTH_GLUSTERFS_v2 and v3 with group and lock-owner lengths near the limit.
