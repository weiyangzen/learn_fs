# sources/distributed-fs/glusterfs/xlators/debug/delay-gen/src/Makefile.am

## Purpose
This Automake file builds and installs the `delay-gen` debug translator module.

## Important APIs, Types, And Functions
It declares `xlator_LTLIBRARIES = delay-gen.la`, installs to `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/debug`, sets module linker flags, uses `delay-gen.c` as the source, links against `libglusterfs.la`, and marks `delay-gen.h`, `delay-gen-mem-types.h`, and `delay-gen-messages.h` as non-installed headers.

## Control Flow
Automake compiles `delay-gen.c` with `GF_CPPFLAGS`, RPC XDR include paths, `-Wall`, `-fno-strict-aliasing`, and `GF_CFLAGS`, then links the loadable xlator module.

## State And Persistence Behavior
No runtime state is held here. It controls produced build artifacts.

## Dependencies And Integration Points
The module depends on libglusterfs and GlusterFS build include variables. Install location matches the translator loader's debug xlator path.

## Risks
Incorrect install path, missing libglusterfs linkage, or missing include paths would produce a module that fails to build or load. Header list drift can break distribution builds.

## Test Signals
Build, install, and module-load tests should confirm `delay-gen` is compiled and discoverable by the GlusterFS xlator loader.
