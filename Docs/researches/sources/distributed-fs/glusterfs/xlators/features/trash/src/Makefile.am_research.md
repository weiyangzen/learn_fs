# sources/distributed-fs/glusterfs/xlators/features/trash/src/Makefile.am

## Purpose
Builds the server-side `trash.la` feature translator module.

## Important APIs, Types, and Functions
- `if WITH_SERVER` gates `xlator_LTLIBRARIES = trash.la`.
- Installs under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`.
- `trash_la_SOURCES = trash.c`.
- `trash_la_LIBADD` links `libglusterfs.la`.
- `noinst_HEADERS = trash.h trash-mem-types.h`.
- `AM_CPPFLAGS` wires libglusterfs and RPC XDR include paths.

## Control Flow
Automake builds a module with `-module $(GF_XLATOR_DEFAULT_LDFLAGS)` when server support is enabled.

## State and Persistence
No runtime state. It controls build artifacts and installation paths.

## Dependencies and Integration Points
Depends on libglusterfs and GlusterFS build variables. The server gate matches trash's brick-side behavior.

## Risks
Missing RPC/libglusterfs include paths or `WITH_SERVER` misconfiguration prevents module build. `trash.c` includes broad Gluster internals, so header dependency churn can break compilation.

## Test Signals
Build `trash.la`; verify module installation under `xlator/features`; run packaging checks for `noinst_HEADERS`.
