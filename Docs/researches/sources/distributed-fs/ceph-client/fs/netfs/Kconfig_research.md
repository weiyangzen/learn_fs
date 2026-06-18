# sources/distributed-fs/ceph-client/fs/netfs/Kconfig

## Purpose

This Kconfig file defines the build-time feature switches for the Linux netfs helper library and FS-Cache manager. It lets filesystems select shared network-filesystem buffered I/O, direct/unbuffered I/O, cache integration, debugging, and optional `/proc` statistics.

## Important Symbols

`NETFS_SUPPORT` is a tristate base option. It enables the `netfs` module or built-in library that provides common high-level helpers for network filesystems, including read segmentation, buffered I/O coordination, local caching hooks, and transparent huge page-oriented pagecache handling.

`NETFS_STATS` is a bool depending on `NETFS_SUPPORT && PROC_FS`. It enables netfs statistics and exposes them through `/proc/fs/fscache/stats`. The help text explicitly calls out cacheline bouncing overhead on multi-CPU systems.

`NETFS_DEBUG` is a bool depending on `NETFS_SUPPORT`. It permits dynamic debug output in netfslib and FS-Cache, controlled through `/sys/module/netfs/parameters/debug`.

`FSCACHE` is a bool depending on `NETFS_SUPPORT`. It enables the generic filesystem local caching manager used by network and other filesystems to cache data locally through pluggable backends.

`FSCACHE_STATS` is a bool depending on `FSCACHE && PROC_FS` and selects `NETFS_STATS`. It enables FS-Cache-specific statistics in the same `/proc/fs/fscache/stats` location.

## Control Flow and Build Behavior

There is no runtime control flow in this file. Its dependency graph constrains which objects the Makefile may include. `FSCACHE` cannot be enabled without `NETFS_SUPPORT`, stats require procfs, and FS-Cache stats automatically select generic netfs stats.

## State and Persistence Behavior

The file creates kernel configuration state, not runtime state. The selected symbols persist in the configured kernel build and determine whether netfs/FS-Cache code, debug knobs, and proc stats exist.

## Dependencies and Integration Points

The main dependencies are Kconfig symbol relationships with `PROC_FS` and netfs users that select or depend on `NETFS_SUPPORT`/`FSCACHE`. Documentation points to `Documentation/filesystems/caching/fscache.rst`. The Makefile consumes these symbols to include `stats.o`, `fscache_*` objects, and proc support.

## Risks and Test Signals

Risk centers on dependency drift: enabling statistics without procfs, FS-Cache without netfs base support, or a filesystem assuming cache APIs exist when `FSCACHE` is disabled. Test signals are kernel config matrix builds with `NETFS_SUPPORT=m/y`, `FSCACHE=n/y`, procfs disabled, stats enabled, and runtime checks for `/proc/fs/fscache/stats` and dynamic debug parameter availability.
