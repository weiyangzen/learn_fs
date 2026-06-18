# sources/distributed-fs/glusterfs/xlators/features/marker/src/Makefile.am

## Purpose
This automake file builds the `marker.la` translator module when server-side translators are enabled. It defines the marker source files, headers, include paths, linker flags, and compiler flags.

## Important APIs, Types, And Functions
The target is `marker.la`, installed under `$(libdir)/glusterfs/$(PACKAGE_VERSION)/xlator/features`. `marker_la_SOURCES` includes `marker.c`, `marker-quota.c`, `marker-quota-helper.c`, and `marker-common.c`. `noinst_HEADERS` includes marker and quota headers plus `libxlator.h`. `marker_la_LIBADD` links against `libglusterfs.la`.

## Control Flow
`if WITH_SERVER` gates whether the xlator library is built. The build compiles with `GF_CPPFLAGS`, `GF_CFLAGS`, include paths for libglusterfs, rpc xdr generated headers, and xlator lib sources.

## State And Persistence Behavior
There is no runtime state. Build outputs are the libtool module and standard automake artifacts.

## Dependencies And Integration Points
The file integrates marker with GlusterFS' translator installation layout and with libglusterfs. Changes here affect whether marker quota code is compiled, packaged, and loadable.

## Risks And Test Signals
Source/header list drift is the main risk: adding a new marker file without updating this file can break builds or omit functionality. Test signals are autotools configure/build success under `WITH_SERVER` and package install path verification.
