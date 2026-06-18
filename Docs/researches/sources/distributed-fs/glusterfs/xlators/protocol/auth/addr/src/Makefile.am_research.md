# sources/distributed-fs/glusterfs/xlators/protocol/auth/addr/src/Makefile.am

## Purpose
Defines the build recipe for the address-based authentication module.

## Important APIs, Types, And Functions
Builds `addr.la` into the Gluster auth module directory from `addr.c`, links `libglusterfs.la`, and includes server, RPC/XDR, and RPC library headers.

## Control Flow
Automake compiles the module with auth-module linker flags.

## State And Persistence
No runtime state. Install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/auth`.

## Dependencies And Integration Points
Uses `authenticate.h` from the protocol server source tree and RPC transport types.

## Risks
Incorrect include paths would break the module's dependency on server authentication interfaces. Wrong `authdir` would prevent dynamic auth loading.

## Test Signals
Build should produce loadable `addr.la`; server auth loading should find it in the auth directory.
