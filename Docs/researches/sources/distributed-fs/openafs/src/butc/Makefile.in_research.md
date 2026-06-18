# sources/distributed-fs/openafs/src/butc/Makefile.in

## Purpose
`Makefile.in` defines the LWP-based Tape Coordinator (`butc`) build, plus the `read_tape` and `tdump` utility targets. It selects the object set, OpenAFS library closure, install behavior, clean rules, and one source-specific compiler flag override.

## Important APIs, Types, And Functions
The key build variables are `INCLS`, `HACKS`, `LIBS`, and `SOBJS`. `SOBJS` builds `butc` from `dbentries.o`, `tcprocs.o`, `lwps.o`, `tcmain.o`, `list.o`, `recoverDb.o`, `tcudbprocs.o`, `dump.o`, and `tcstatus.o`. `LIBS` links BUDB, BUTM, volume, VLDB, protection/authentication, Ubik, Rx, audit, LWP, command, error, crypto, USD, util, OPR, and process-management libraries. `CFLAGS_tcudbprocs.o=@CFLAGS_NOERROR@` relaxes error handling for that object.

## Control Flow
The default `all` target builds `butc`, `read_tape`, and `tdump`. `butc` uses `AFS_LDRULE_NOQ`, with a special AIX branch that links `/usr/lib/libc_r.a`. `read_tape` and `tdump` are built directly from their C files. `install` and `dest` create target directories and install `read_tape` everywhere, but skip installing this `butc` binary on platforms where `tbutc` supplies the installed coordinator, except older Darwin variants and fallback systems.

## State And Persistence
The makefile persists no runtime state, but it determines which coordinator implementation and tools are installed into `sbindir` or `${DEST}/etc`. The install platform gates are operationally important because a system may build this target but intentionally not deploy it.

## Dependencies And Integration Points
It includes generated configuration makefiles from `@TOP_OBJDIR@/src/config`, `Makefile.lwp`, and `../config/Makefile.version`. Its library ordering encodes the coordinator's integration with BUDB, volume services, authentication, Rx/Ubik, tape/media handling, and command/audit infrastructure.

## Risks And Test Signals
Risks include stale library ordering, platform install drift, and object lists diverging from source dependencies. Build tests should verify `butc`, `read_tape`, and `tdump` on representative non-XBSA and platform-gated environments. Packaging tests should confirm that install/dest skip or install `butc` exactly as intended for Linux, Solaris, AIX, HP-UX, Darwin, and fallback systems.
