# sources/distributed-fs/glusterfs/xlators/debug/io-stats/src/Makefile.am

## Purpose
Builds and installs the `io-stats` xlator shared module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-stats.la` declares the module, with `xlatordir` targeting `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/debug`. `io_stats_la_SOURCES = io-stats.c` and `noinst_HEADERS = io-stats-mem-types.h` define the source set. `io_stats_la_LIBADD` links against `libglusterfs.la`. `AM_CPPFLAGS` adds libglusterfs, generated RPC/XDR, rpc-lib include paths, and defines `DATADIR` from `$(localstatedir)`. `AM_CFLAGS` adds warning and GlusterFS C flags.

## Control flow
The autotools build compiles `io-stats.c` with the listed include paths, links a module with default xlator LDFLAGS, and installs it under the debug xlator directory for runtime graph loading.

## State and persistence behavior
No runtime state is stored here. The `DATADIR` macro affects runtime dump paths in `io-stats.c`, so packaging/localstatedir choices influence where periodic stats files are created.

## Dependencies and integration points
Integrates with the GlusterFS module build system, libtool, libglusterfs, and generated RPC/XDR headers. The noinst memory header is private to this module.

## Risks and test signals
Risks include missing include paths for generated RPC headers and incorrect `DATADIR` causing dump files to land in the wrong local-state tree. Test by building the target and verifying `io-stats.la` links and installs to the expected xlator path.
