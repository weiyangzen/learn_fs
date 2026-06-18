# sources/distributed-fs/glusterfs/xlators/performance/readdir-ahead/src/Makefile.am

## Purpose
Defines the build recipe for the `readdir-ahead` xlator module.

## Important APIs, Types, And Functions
Builds `readdir-ahead.la` into the performance xlator directory. Sources are `readdir-ahead.c`; private headers are `readdir-ahead.h`, `readdir-ahead-mem-types.h`, and `readdir-ahead-messages.h`. Links against `libglusterfs.la`.

## Control Flow
Automake compiles the single C source with Gluster and RPC/XDR include paths and module linker flags.

## State And Persistence
No runtime state. It controls installed module location under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## Dependencies And Integration Points
Depends on `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, libglusterfs, and XDR headers.

## Risks
Missing headers from `noinst_HEADERS` would not be distributed to builds. Incorrect `xlatordir` would install the translator into the wrong category.

## Test Signals
Build output should produce a loadable `readdir-ahead.la` module with no unresolved libglusterfs symbols.
