# sources/distributed-fs/moosefs/mfschunkserver/Makefile.am

## Purpose
`Makefile.am` is the Automake source for the MooseFS chunkserver directory. It declares the programs installed into `sbin` and the source/link composition for `mfschunkserver`, `mfschunktool`, `mfscsstatsdump`, and `mfschunkdbdump`. It is the maintainable build contract that generates the much larger `Makefile.in`.

## Important Build Targets and Variables
The key exported target set is `sbin_PROGRAMS = mfschunkserver mfschunktool mfscsstatsdump mfschunkdbdump`. `AM_CPPFLAGS` points local targets at `$(top_srcdir)/mfscommon`, while target-specific flags add dependency libraries. `mfschunkserver_CPPFLAGS` defines `MFSMAXFILES=16384`, `_USE_PTHREADS`, `APPNAME=mfschunkserver`, `USE_CONNCACHE`, and `USE_IONICE`; its CFLAGS/LDFLAGS pull in pthread, dynamic linker, zlib, and math libraries through configure substitutions.

`mfschunkserver_SOURCES` is the integration inventory for the daemon: local chunkserver modules (`bgjobs`, `csserv`, `mainserv`, `hddspacemgr`, `masterconn`, `busychunks`, `replicator`, `chartsdata`, `chartsdefs`, `init`) plus many `mfscommon` support modules for event-loop startup, config, queues, threading, CRC, sockets, connection cache, charts, memory and CPU accounting, logging, and protocol definitions. `mfscsstatsdump_SOURCES` reuses `chartsdefs.h` and common chart/stat dump helpers so the stats dump tool uses the same chart schema as the daemon.

## Control Flow and Integration
Automake consumes this file to produce `Makefile.in`; configure then instantiates a concrete `Makefile`. Runtime control flow is not here, but build-time dependency flow is: adding a chunkserver module without listing it in `mfschunkserver_SOURCES` excludes it from the daemon, while adding chart metrics without `chartsdefs.h` in the stats dump target would desynchronize dump tooling from daemon persistence.

## State and Persistence
The file does not persist runtime state. Its persistent effect is generated build metadata and installed binaries. `distclean-local` removes `./$(DEPDIR)` and `Makefile`, matching Automake cleanup expectations.

## Dependencies
This file depends on Autoconf/Automake substitutions for `PTHREAD_*`, `ZLIB_LIBS`, `MATH_LIBS`, and `DYNLINKER_FLAGS`. It depends structurally on `../mfscommon` for common daemon infrastructure and on local chunkserver modules for the daemon itself.

## Risks
The main risk is build drift: `Makefile.am` must remain the source of truth, or regenerated `Makefile.in` will overwrite manual generated-file edits. Target-specific CPPFLAGS are behaviorally important; dropping `_USE_PTHREADS`, `USE_CONNCACHE`, or `USE_IONICE` can alter threading, connection cache, or I/O scheduling paths. The stats dump tool depends on the exact chart definitions, so chart schema changes should update both daemon and tool source lists.

## Test Signals
Useful signals are a successful `autoreconf`/Automake regeneration, `./configure && make` in this subtree or repository, target link success for all four `sbin_PROGRAMS`, and `make distclean` removing generated dependency directories without leaving stale `Makefile` state.
