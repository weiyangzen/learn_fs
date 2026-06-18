# sources/distributed-fs/glusterfs/xlators/performance/io-cache/src/Makefile.am

## Purpose
Builds the `io-cache` performance translator as a loadable GlusterFS xlator module.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = io-cache.la` declares the plugin. `io_cache_la_SOURCES` compiles `io-cache.c`, `page.c`, and `ioc-inode.c`. `noinst_HEADERS` tracks `io-cache.h`, `ioc-mem-types.h`, and `io-cache-messages.h`. `io_cache_la_LIBADD` links against `libglusterfs.la`.

## Control flow
Autotools compiles the three C files, links a module with `GF_XLATOR_DEFAULT_LDFLAGS`, and installs it under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/performance`.

## State and persistence behavior
No runtime state is stored. The file fixes the module name, install location, include path surface, and linkage.

## Dependencies and integration points
Depends on libglusterfs headers, generated RPC/XDR include directories, and the contrib rbtree path because io-cache uses `rbthash`. The installed module is discovered by Gluster's translator loader and volfile parser.

## Risks and test signals
Risks include omitting one of the three cooperative implementation files, missing rbtree include paths, or creating a module that links but lacks required xlator symbols. Test signals include successful module build, symbol presence for `xlator_api`, and runtime load of `performance/io-cache`.
