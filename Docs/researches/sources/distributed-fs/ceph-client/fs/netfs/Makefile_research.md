# sources/distributed-fs/ceph-client/fs/netfs/Makefile

## Purpose

This Makefile assembles the `netfs.o` composite object for the shared network-filesystem support library. It maps Kconfig selections to the core netfs read/write, object, locking, retry, rolling-buffer, and optional FS-Cache objects.

## Important Build Units

The unconditional `netfs-y` list includes buffered read/write, direct read/write, iterator helpers, I/O locking, module initialization, miscellaneous wait/folio helpers, object allocation, read collection, page-private copy-to-cache support, read retry/single-read, rolling buffer, write collection, write issue, and write retry. This establishes that the base netfs library includes both buffered and unbuffered paths plus shared request lifecycle and collection machinery.

`netfs-$(CONFIG_NETFS_STATS) += stats.o` adds generic statistics only when enabled. `netfs-$(CONFIG_FSCACHE)` adds cache, cookie, I/O, main, and volume FS-Cache objects. `fscache_proc.o` is included only when both procfs and FS-Cache are enabled, and `fscache_stats.o` is included with `CONFIG_FSCACHE_STATS`.

`obj-$(CONFIG_NETFS_SUPPORT) += netfs.o` makes the composite object built-in, modular, or absent according to `NETFS_SUPPORT`.

## Control Flow and State

There is no runtime control flow. The file defines link composition and therefore which symbols are available at runtime. Because `netfs.o` is composite, optional objects participate in the same module/built-in image as the base helpers.

## Dependencies and Integration Points

The Makefile integrates with Kbuild composite-object conventions and the symbols defined in `Kconfig`. It is an important integration point for netfs users such as CephFS because missing objects mean missing exports or disabled caching/statistics behavior.

## Risks and Test Signals

Risks include forgetting to add a new object to `netfs-y`, accidentally putting a core dependency behind `CONFIG_FSCACHE`, or creating unresolved symbols in config combinations. Test signals are `allmodconfig`, `allyesconfig`, minimal configs with `CONFIG_NETFS_SUPPORT=n`, `m`, and `y`, and build tests with FS-Cache and procfs independently toggled.
