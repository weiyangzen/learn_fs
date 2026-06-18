# sources/distributed-fs/glusterfs/xlators/performance/write-behind/src/Makefile.am

## Purpose
Defines the build recipe for the `write-behind` xlator module.

## Important APIs, Types, And Functions
Builds `write-behind.la` into the performance xlator directory from `write-behind.c`, links `libglusterfs.la`, and declares `write-behind-mem-types.h` and `write-behind-messages.h` as private headers.

## Control Flow
Automake compiles the module with Gluster and RPC/XDR include paths and module linker flags.

## State And Persistence
No runtime state. Install path is `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## Dependencies And Integration Points
Depends on `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, and libglusterfs.

## Risks
Missing source/header entries can break distribution builds. Wrong install directory would prevent graph loading by category/name.

## Test Signals
Build should produce `write-behind.la` with no unresolved Gluster symbols.
