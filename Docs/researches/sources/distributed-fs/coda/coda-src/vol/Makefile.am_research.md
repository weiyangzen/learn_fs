# sources/distributed-fs/coda/coda-src/vol/Makefile.am

## Purpose

`sources/distributed-fs/coda/coda-src/vol/Makefile.am` defines the automake build for the Coda volume package library, which is compiled when `BUILD_SERVER` is enabled.

## Important APIs, Types, and Functions

It builds `libvol.la` from directory vnode, cached vnode, volume, utility, VLDB, fssync, index, recovery, volume hash, dump, VRDB, vlist, lock queue, allocation, debug, lock, tree-remove, globals, definitions, resolution, and structure sources/headers. It installs/distributes the `vrdb.5` man page under server builds and includes `testvrdb.cc` as extra distribution content.

## Control Flow

There is no runtime flow. Build-time flow is controlled by `BUILD_SERVER`; when enabled, automake compiles the volume package with RVM/RPC2 flags and include paths for base, kerndep, util, vicedep, dir, ACL, partition, auth2, version-vector, and lookaside modules.

## State and Persistence Behavior

No runtime state is stored here. The file determines which implementation files participate in the volume package that manages persistent volume headers, vnode indexes, RVM recovery, volume hash tables, and related server state.

## Dependencies and Integration Points

It depends on `$(RVM_RPC2_CFLAGS)`, source and build directories for generated `vicedep`/`auth2` headers, and server-only build configuration. It integrates the volume package into the broader server build.

## Risks and Edge Cases

Omitting a source/header from `libvol_la_SOURCES` can break distribution tarballs or incremental builds even if local includes happen to work. Build order depends on generated headers in `coda-src/vicedep` and `auth2`. Client-only builds must not accidentally reference `libvol.la`.

## Test Signals

Run server-enabled configure/build, distribution checks, and clean-tree rebuilds; verify generated include directories exist before compiling volume sources; run volume package unit/smoke tests such as VRDB tests.
