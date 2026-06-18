# sources/distributed-fs/glusterfs/xlators/protocol/client/src/Makefile.am

## Purpose
Defines the build recipe for the Gluster protocol client xlator.

## Important APIs, Types, And Functions
Builds `client.la` from `client.c`, helpers, RPC fops, handshake, callback, and common files. Links libglusterfs, gfrpc, and gfxdr. Private headers include `client.h`, memory/message headers, and `client-common.h`.

## Control Flow
Automake compiles all client sources with libglusterfs, RPC/XDR, socket transport, and RPC library include paths.

## State And Persistence
No runtime state. Install path is `xlator/protocol`.

## Dependencies And Integration Points
This module is the client-side protocol endpoint and depends on Gluster core, RPC transport, XDR generated protocol types, and callback handling in `client-callback.c`.

## Risks
The source list must stay synchronized with generated protocol and helper files. Missing RPC libraries would surface as link failures.

## Test Signals
Build should produce loadable `client.la`; protocol handshake and callback actor symbols should resolve.
