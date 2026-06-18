# sources/distributed-fs/glusterfs/xlators/features/sdfs/src/Makefile.am

## Purpose
This automake file builds the SDFS feature translator module when server-side components are enabled.

## Important APIs and Build Targets
- `if WITH_SERVER` gates `xlator_LTLIBRARIES = sdfs.la`.
- `sdfs_la_SOURCES = sdfs.c`.
- `sdfs_la_LIBADD` links `libglusterfs.la`.
- `noinst_HEADERS` includes `sdfs.h`, `sdfs-messages.h`, and `libxlator.h`.
- `AM_CPPFLAGS` includes libglusterfs, xlators/lib, and RPC XDR headers.
- `AM_CFLAGS = -Wall -fno-strict-aliasing $(GF_CFLAGS)`.

## Control Flow
There is no runtime flow. Build-time conditional `WITH_SERVER` controls whether the SDFS translator is produced.

## State and Persistence
No runtime state. Build output is a loadable `sdfs.la` module under the GlusterFS feature xlator directory.

## Dependencies and Integration Points
Depends on the GlusterFS build system, libglusterfs, libxlator headers, and RPC XDR headers. The message header researched in this subset is packaged as a non-installed implementation header.

## Risks
Server-only gating means client-only builds will not compile SDFS, potentially hiding compile drift until server builds run. Header dependencies must stay aligned with `sdfs.c`.

## Test Signals
Run build with `WITH_SERVER` enabled to catch compile/link issues. Packaging tests should confirm `sdfs.la` is produced only in server builds.
