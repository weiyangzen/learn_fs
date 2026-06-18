# sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h

## Purpose

`sources/distributed-fs/ceph-client/fs/lockd/nlm4xdr_gen.h` is the generated declaration header for NLMv4 server-side XDR wrappers. The source was read as a complete 32-line generated file.

## Important APIs, Types, and Functions

It declares all public decode and encode wrappers implemented by `nlm4xdr_gen.c`, including void, lock/test/cancel/unlock/testres/res/notify/share decoders and void/testres/res/shareres encoders.

## Control Flow

There is no executable flow. Server dispatch code includes this header to bind procedure descriptors to generated XDR wrapper functions.

## State and Persistence Behavior

No state is owned. The header only exposes function prototypes and generated type dependencies.

## Dependencies and Integration Points

The header includes SUNRPC XDR APIs, xdrgen builtin definitions, and generated NLMv4 protocol type definitions. It must match `nlm4xdr_gen.c` and the `.x` source.

## Risks and Edge Cases

Generated declaration drift will break server builds or, worse, mismatch expected argument/response buffers. Manual edits will be lost.

## Test Signals

Build coverage for `CONFIG_LOCKD_V4`, regeneration diff checks, and server procedure table compilation against these prototypes.
