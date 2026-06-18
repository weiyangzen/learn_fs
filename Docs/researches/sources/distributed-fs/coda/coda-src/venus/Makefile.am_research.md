# sources/distributed-fs/coda/coda-src/venus/Makefile.am

## Purpose
This Automake input defines the Venus client build targets, installed man pages/config files, Venus source list, compiler include paths, and link dependencies.

## Important APIs, Types, and Functions
`sbin_PROGRAMS` conditionally includes `vutil` under `BUILD_CLIENT` and `venus` under `BUILD_VENUS`. `venus_SOURCES` enumerates the Venus implementation, including `archive.c`, `9pfs.cc`, and `SpookyV2.cc`. `AM_CPPFLAGS` defines `VENUS`, timing/debug macros, and include paths across base, kernel dependency, util, dir, auth, vv, lka, vol, and repair libraries. `venus_LDADD` links repair, lka, vv, codadir, venusdep, util, rwcdb, base, and RPC2/RVM dependencies.

## Control Flow
Build-time conditionals select installed programs and man/config data. Automake expands the source and library lists into generated Makefile rules.

## State and Persistence Behavior
No runtime state is managed. Build configuration determines whether Venus, vutil, `venus.conf.ex`, and `realms` are installed.

## Dependencies and Integration Points
The file integrates with top-level configure options `BUILD_CLIENT` and `BUILD_VENUS`, generated build directories, and libraries used by the Venus daemon.

## Risks and Test Signals
Risks are missing source additions, stale include paths, and link-order regressions. Test signals are successful `make` with client-only, Venus-enabled, and both-disabled configurations, plus distribution checks ensuring installed config/man files are included.
