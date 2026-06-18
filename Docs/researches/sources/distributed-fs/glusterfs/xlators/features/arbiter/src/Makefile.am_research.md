<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am -->
# sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am

## Purpose
Build recipe for the arbiter translator shared object.

## APIs, Types, and Functions
When `WITH_SERVER` is enabled, builds `arbiter.la` as an xlator module under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. Sources are `arbiter.c`; private headers are `arbiter.h` and `arbiter-mem-types.h`; it links `libglusterfs.la`.

## Control Flow, State, and Persistence
Automake compiles the translator with GlusterFS include paths, XDR include paths, `GF_CPPFLAGS`, `GF_CFLAGS`, and `-Wall`. Runtime behavior lives in `arbiter.c`.

## Dependencies and Integration
Depends on the server build toggle, libglusterfs, and generated RPC/XDR headers. The installed module is loaded by volume graphs using the `features/arbiter` xlator.

## Risks and Test Signals
Risks include server-disabled builds omitting the translator and include path drift for XDR/libglusterfs headers. Test signals are module build, installation path correctness, and loading the module in a server-enabled volume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/features/arbiter/src/Makefile.am -->
