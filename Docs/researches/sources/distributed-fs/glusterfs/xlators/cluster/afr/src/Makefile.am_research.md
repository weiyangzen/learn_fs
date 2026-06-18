# sources/distributed-fs/glusterfs/xlators/cluster/afr/src/Makefile.am

## Purpose

This Automake file builds and installs the AFR replication translator module. It produces `afr.la` under the cluster translator installation directory and installs a compatibility symlink from `replicate.so` to `afr.so`.

## Important build variables and targets

- `AUTOMAKE_OPTIONS = subdir-objects` allows object paths for sources outside the local directory, notably `$(top_builddir)/xlators/lib/src/libxlator.c`.
- `xlator_LTLIBRARIES = afr.la` declares the translator module.
- `xlatordir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/cluster` sets the install directory.
- `afr_common_source` includes AFR operation families (`afr-dir-read.c`, `afr-dir-write.c`, `afr-inode-read.c`, `afr-inode-write.c`, `afr-open.c`, `afr-transaction.c`, `afr-lk-common.c`, `afr-read-txn.c`) and `libxlator.c`.
- `AFR_SELFHEAL_SOURCES` includes common, data, entry, metadata, daemon, and name self-heal sources.
- `afr_la_SOURCES = $(afr_common_source) $(AFR_SELFHEAL_SOURCES) afr.c`; `afr.c` includes `afr-common.c`, so `afr-common.c` is listed in `noinst_HEADERS` rather than compiled as a separate source.
- `afr_la_LIBADD = $(top_builddir)/libglusterfs/src/libglusterfs.la`.
- `AM_CPPFLAGS` adds libglusterfs, xlator library, RPC, and generated XDR include directories from both source and build trees.
- `install-data-hook` creates `replicate.so -> afr.so`; `uninstall-local` removes the compatibility symlink.

## Control flow and integration

The generated build compiles AFR's module sources into a libtool module with GlusterFS's default xlator linker flags. The symlink hook preserves the older translator name `replicate.so` for volume graphs or tooling that still refer to "replicate" while the actual module is built as `afr.so`.

## State and persistence behavior

Runtime persistence is not managed here. The file determines installed module artifacts under the versioned GlusterFS translator directory and creates/removes the `replicate.so` symlink during install/uninstall.

## Dependencies and integration points

AFR depends on `libglusterfs.la`, local AFR headers, `xlators/lib/src/libxlator.h`, RPC/XDR headers, and generated XDR build output. It integrates with the broader translator ABI through `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, `GF_CFLAGS`, and the installed module layout consumed by Gluster volume graphs.

## Risks and edge cases

- `afr-common.c` is included by `afr.c`; adding it to `afr_la_SOURCES` as a normal C source would likely duplicate symbols.
- The symlink hook assumes the installed module name is `afr.so`; libtool naming or install-layout changes could break `replicate.so`.
- Include order includes both source and build XDR directories; stale generated headers in the build tree can mask source-tree changes.
- `libxlator.c` is pulled from `top_builddir`, so out-of-tree builds rely on `subdir-objects` and correct generated paths.

## Test signals

Run recursive `make` for `xlators/cluster/afr/src`, inspect that `afr.la`/`afr.so` is produced, and run `make install DESTDIR=...` to verify `cluster/afr.so` and `cluster/replicate.so` symlink creation. A clean uninstall should remove the symlink. Functional tests should exercise AFR volume loading by both current and compatibility translator names.
