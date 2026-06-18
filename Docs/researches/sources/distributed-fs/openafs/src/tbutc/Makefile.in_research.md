# sources/distributed-fs/openafs/src/tbutc/Makefile.in

## Purpose
`src/tbutc/Makefile.in` builds the pthread backup tape coordinator `butc` and the local `libbutm.a` media library from butc, butm, bucoord, and volser sources.

## Important APIs, types, and functions
Key targets are `all`, `butc`, `libbutm.a`, object rules for butc modules (`tcmain`, `tcprocs`, `dump`, `lwps`, `dbentries`, `recoverDb`, `tcstatus`, XBSA support), bucoord helpers, volser helpers, `install`, `dest`, and `clean`.

## Control flow
The makefile compiles selected source files from sibling directories with `AFS_CCRULE`, applies `CFLAGS_NOERROR` to `tcudbprocs.o`, archives `libbutm.a`, and links `butc` against budb, bubasics, butm, kauth, volser, vldb, ubik, rxkad, cmd, util, opr, usd, LWP compatibility, sys, and process-management libraries.

## State and persistence behavior
It writes object files, `libbutm.a`, `butc`, component version output, and install/dest copies under configured server binary locations. `clean` removes build outputs.

## Dependencies and integration points
It integrates the backup tape coordinator with backup database, volume server, ubik, rxkad, USD, XBSA flags, and configured top include/lib directories.

## Risks
Cross-directory source ownership makes dependency drift easy. Library ordering and optional XBSA flags can break only in specific configurations. Suppressing errors for `tcudbprocs.o` may hide warnings that should be fixed.

## Test signals
Build with and without XBSA flags, run `make butc`, verify `libbutm.a`, and test install/dest paths. Functional signals include backup dump/restore smoke tests against a test cell.
