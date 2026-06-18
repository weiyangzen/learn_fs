# sources/distributed-fs/glusterfs/xlators/meta/src/Makefile.am

## Purpose
Builds the `meta.la` xlator, which exposes GlusterFS runtime introspection as a virtual metadata filesystem.

## Important APIs, Types, and Functions
- Installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator`.
- `meta_la_SOURCES` enumerates core meta files plus many virtual file/dir/link implementations.
- Links `libglusterfs.la`.
- `noinst_HEADERS` include `meta.h`, `meta-hooks.h`, and `meta-mem-types.h`.
- Include paths cover libglusterfs and RPC XDR headers.

## Control Flow
Automake compiles all listed virtual-node implementations into one module.

## State and Persistence
No direct runtime state; controls build artifacts.

## Dependencies and Integration Points
Depends on libglusterfs and meta source files. The requested source files in this group are entries in `meta_la_SOURCES`.

## Risks
Omitting a virtual node implementation breaks hook references or removes introspection files. Adding a new meta node requires updating this source list.

## Test Signals
Build `meta.la`, load the meta translator, and inspect that listed virtual files/dirs appear.
