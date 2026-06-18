# sources/distributed-fs/glusterfs/xlators/mount/fuse/src/Makefile.am

## Purpose

This Automake file builds the GlusterFS FUSE mount translator module `fuse.la`. It selects platform-specific FUSE mount support sources and headers, compiles the core FUSE bridge and helper sources, and installs the module under the Gluster translator directory.

## Important Build Variables and Targets

- `AUTOMAKE_OPTIONS = subdir-objects` allows source files from contrib directories to produce object files under corresponding subdirectories.
- `noinst_HEADERS_common` lists common FUSE translator headers and contrib FUSE headers.
- `noinst_HEADERS_linux` includes Linux FUSE kernel and mount utility headers.
- `noinst_HEADERS_darwin` includes MacFUSE-specific headers.
- The `GF_DARWIN_HOST_OS` conditional chooses the installed noinst header set and the `mount_source`.
- `xlator_LTLIBRARIES = fuse.la` declares the translator module.
- `xlatordir = $(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/mount` sets the install location for the mount translator.
- `fuse_la_SOURCES` includes `fuse-helpers.c`, `fuse-resolve.c`, `fuse-bridge.c`, contrib FUSE `misc.c`, and the platform-selected mount source.
- `fuse_la_LDFLAGS = -module $(GF_XLATOR_DEFAULT_LDFLAGS)` builds the output as a loadable translator module.
- `fuse_la_LIBADD` links against `libglusterfs.la`, `$(GF_LDADD)`, and configured FUSE linker flags `@GF_FUSE_LDADD@`.
- `AM_CPPFLAGS` adds Gluster core include paths, generated XDR include paths, contrib FUSE include paths, and `$(GF_FUSE_CFLAGS)`.
- `AM_CFLAGS = -Wall $(GF_CFLAGS)` applies common compiler flags and warnings.

## Control Flow and Integration

The build creates a loadable xlator module consumed by Gluster's client/mount stack. Platform conditionals select `$(CONTRIBDIR)/macfuse/mount_darwin.c` on Darwin and `$(CONTRIBDIR)/fuse-lib/mount.c` plus `mount-common.c` elsewhere. The core translator sources bridge kernel/userspace FUSE requests into GlusterFS client operations, while contrib mount sources provide the OS-specific mount interface.

Generated XDR include paths from both source and build trees allow the module to include RPC protocol headers regardless of in-tree or out-of-tree builds. The final module is installed in the versioned Gluster xlator directory so runtime translator loading can locate it.

## State and Persistence Behavior

There is no runtime state in this Makefile, but it defines persistent build/install artifacts: object files, the `fuse.la` libtool module, and the installed translator under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/mount`. Changing `xlatordir`, source lists, or linker flags changes what the runtime loader can find.

## Dependencies

The build depends on libtool/Automake, `libglusterfs`, generated RPC/XDR headers, contrib FUSE and MacFUSE source trees, configured FUSE compiler and linker flags, and platform conditionals from configure. It also relies on `GF_XLATOR_DEFAULT_LDFLAGS`, `GF_CPPFLAGS`, `GF_CFLAGS`, `GF_LDADD`, `CONTRIBDIR`, and `PACKAGE_VERSION`.

## Risks and Edge Cases

- Incorrect `GF_DARWIN_HOST_OS` detection selects the wrong mount source and header set.
- Missing `@GF_FUSE_LDADD@` or `$(GF_FUSE_CFLAGS)` values can compile but fail link, or fail to find the host FUSE ABI.
- Out-of-tree builds require both source and build XDR include paths; removing either can break generated-header discovery.
- Because contrib sources are compiled into this module, path and distribution rules must keep contrib FUSE/MacFUSE files available.
- Runtime module discovery depends on `xlatordir` matching Gluster's versioned translator lookup path.

## Test Signals

Validation should include Linux and Darwin configure/build jobs, out-of-tree builds, `make distcheck`, and runtime smoke tests that mount a Gluster volume through FUSE and verify the `fuse` translator module is installed under the expected versioned xlator path. Link tests should confirm the configured FUSE libraries are actually present and compatible.
