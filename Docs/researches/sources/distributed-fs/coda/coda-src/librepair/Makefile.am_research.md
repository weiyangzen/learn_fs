# sources/distributed-fs/coda/coda-src/librepair/Makefile.am

## Purpose
Automake rules for Coda repair libraries.

## APIs, Types, and Functions
Builds `librepio.la` from `repio.cc`/`repio.h` and `libclnrepair.la` from `resolve.cc`, `resolve.h`, `cure.cc`, `cure.h`, `predicate.cc`, `predicate.h`, `repcmds.cc`, `repcmds.h`, `rvol.cc`, and `path.cc`. Include paths cover RPC2, base, kerndep, util, vicedep, al, partition, auth2, vv, and vol.

## Control Flow, State, and Persistence
No runtime flow. It groups repair I/O, conflict resolution, predicate/cure logic, path processing, and volume replica helpers into libraries.

## Dependencies and Integration
Used by repair clients and command tools that need non-interactive repair operations and fix-file processing.

## Risks and Test Signals
Risks include broad include coupling and split libraries whose consumers must link the right one. Test signals are successful build and downstream repair command linkage.
