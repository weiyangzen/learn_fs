# sources/distributed-fs/glusterfs/xlators/protocol/server/src/Makefile.am

## Purpose

This automake file builds the protocol/server xlator module. It declares `server.la` conditionally under `WITH_SERVER`, lists source and installed header files, and wires library and include dependencies needed for the server-side RPC protocol implementation.

## Important APIs, types, and functions

The module sources are `server.c`, `server-resolve.c`, `server-helpers.c`, `server-handshake.c`, `authenticate.c`, `server-common.c`, and `server-rpc-fops_v2.c`. Installed headers are `server.h`, `server-helpers.h`, `server-mem-types.h`, `authenticate.h`, `server-messages.h`, and `server-common.h`. Link inputs are libglusterfs, gfrpc, gfxdr, and `LIB_DL`, the last of which is required by dynamic authentication module loading in `authenticate.c`.

## Control flow

When `WITH_SERVER` is true, automake builds `server.la` as a module using `-module` and GlusterFS's default xlator LDFLAGS. Compile flags define `CONFDIR`, `LIBDIR` for authentication modules, and `DATADIR`, and add include paths for libglusterfs, socket transport, protocol lib, rpc-lib, XDR build/source trees, and glusterfsd.

## State and persistence behavior

There is no runtime state here, but the compile-time `LIBDIR` constant determines where `authenticate.c` looks for auth modules at runtime. The install paths place the xlator under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/protocol` and headers under `$(includedir)/glusterfs/server`.

## Dependencies and integration points

The file connects protocol/server to GlusterFS's core library, RPC stack, generated XDR code, dynamic loader, and socket transport. It is also the source of truth for which server implementation files are compiled into the module.

## Risks and test signals

Risks include missing `LIB_DL`, stale source/header lists, incorrect generated-XDR include paths, and mismatched `LIBDIR` causing authentication modules to fail at runtime. Build tests should check `WITH_SERVER` on/off, `make dist`, installation layout, and a runtime authentication module load.
