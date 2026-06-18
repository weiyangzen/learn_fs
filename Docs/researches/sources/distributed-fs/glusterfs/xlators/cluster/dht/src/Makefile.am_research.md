# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/Makefile.am

## Purpose
This automake file defines the build for GlusterFS DHT-family cluster translators: `dht.la`, `nufa.la`, and `switch.la`. It collects the common DHT source set, adds the translator-specific entry source for each module, sets compiler and include flags, links against `libglusterfs.la`, installs modules into the GlusterFS cluster xlator directory, and creates a compatibility symlink from `distribute.so` to `dht.so`.

## Important APIs, Types, And Functions
Important automake variables include `xlator_LTLIBRARIES`, `xlatordir`, `dht_common_source`, `dht_la_SOURCES`, `nufa_la_SOURCES`, `switch_la_SOURCES`, per-library `*_LDFLAGS` and `*_LIBADD`, `noinst_HEADERS`, `AM_CFLAGS`, `AM_CPPFLAGS`, `CLEANFILES`, `uninstall-local`, `install-data-hook`, and the `if UNITTEST` conditional block.

The common source list includes layout, helper, linkfile, rebalance, self-heal, rename, hash, disk-usage, common, inode read/write, shared, lock, and `libxlator.c` sources. Module-specific sources are `dht.c`, `nufa.c`, and `switch.c`. Headers include `dht-common.h`, `dht-mem-types.h`, `dht-messages.h`, `dht-lock.h`, and `libxlator.h`.

## Control Flow
Automake builds all three libtool modules from the shared source list plus one entry source. The modules use `-module` and `$(GF_XLATOR_DEFAULT_LDFLAGS)`, link to the built `libglusterfs.la`, and install into `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/cluster`. `install-data-hook` creates `distribute.so` as a symlink to `dht.so`; `uninstall-local` removes that symlink. If `UNITTEST` is enabled, coverage and xunit artifacts are added to `CLEANFILES`, while `noinst_PROGRAMS` and `TESTS` are initialized empty for this makefile.

## State And Persistence
This file has no runtime state. Build-time state consists of generated `.la`, `.so`, object, coverage, and optional test result files. Installation persists the DHT/Nufa/Switch translator modules and the legacy `distribute.so` symlink in the target xlator directory. The `DATADIR` and `LIBDIR` preprocessor defines embed configured paths into compiled code.

## Dependencies And Integration Points
It depends on GlusterFS build variables (`GF_CFLAGS`, `GF_CPPFLAGS`, `GF_XLATOR_DEFAULT_LDFLAGS`, `PACKAGE_VERSION`), the top-level build directory for `libglusterfs.la` and `libxlator.c`, source-tree include directories for libglusterfs, RPC XDR, RPC library, and xlator lib, and automake/libtool conventions for `xlator_LTLIBRARIES`. The source list integrates DHT code with the shared xlator support library and exposes three translator variants from the same implementation base.

## Risks
Because `dht_common_source` is shared by all three modules, adding a source or header needed by only one variant can accidentally affect all variants or fail another module's build. The compatibility symlink assumes `dht.so` exists at install time and `ln -sf` is acceptable for the target filesystem/package manager. Paths reference both top source and top build trees; generated headers or out-of-tree builds can fail if include ordering is wrong. The unit-test conditional currently declares empty test lists, so enabling `UNITTEST` here alone may not execute DHT tests.

## Test Signals
Build signals include successful out-of-tree and in-tree autotools builds of `dht.la`, `nufa.la`, and `switch.la`, correct linkage to `libglusterfs.la`, and successful install/uninstall of the `distribute.so` symlink. Packaging checks should inspect module placement under `xlator/cluster`. Developer tests should verify that changing the common source list rebuilds all three modules and that `make clean` removes coverage artifacts when `UNITTEST` is set.
