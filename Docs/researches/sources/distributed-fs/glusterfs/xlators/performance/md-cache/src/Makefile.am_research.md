# sources/distributed-fs/glusterfs/xlators/performance/md-cache/src/Makefile.am

## Purpose
Builds the `md-cache` translator and installs a compatibility symlink named `stat-prefetch.so`.

## Important APIs, types, and functions
`xlator_LTLIBRARIES = md-cache.la` declares the plugin. `md_cache_la_SOURCES = md-cache.c` builds the implementation. `noinst_HEADERS` includes memory and message headers. `stat-prefetch-compat` removes any old `stat-prefetch.so` and symlinks it to `./md-cache.so`; `install-exec-local` invokes that rule and `uninstall-local` removes the symlink.

## Control flow
The module is compiled and linked against `libglusterfs.la`, installed to the performance xlator directory, and the compatibility symlink is created during install.

## State and persistence behavior
No runtime state is managed, but install state includes the `stat-prefetch.so` symlink for older volfiles or tooling.

## Dependencies and integration points
Depends on libglusterfs, generated RPC/XDR include paths, contrib rbtree includes, and install-time filesystem operations. Integrates with Gluster's translator loader under both `md-cache` and legacy `stat-prefetch` names.

## Risks and test signals
Risks include a broken relative symlink, stale compatibility module on uninstall, missing headers from distribution, and loader failures under legacy names. Tests should cover clean install/uninstall, symlink target validity, module load as `performance/md-cache`, and legacy `performance/stat-prefetch` load.
