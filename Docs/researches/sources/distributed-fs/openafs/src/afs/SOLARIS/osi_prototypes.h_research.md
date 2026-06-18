# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_prototypes.h

## Purpose
Solaris OSI prototype header for platform functions shared across Solaris source files.

## Important APIs, Types, and Functions
Declares `afs_putpage`, `afs_putapage`, and `afs_xsetgroups`, with Solaris 11 signature variants using `caller_context_t` and `int64_t` syscall returns.

## Control Flow
No runtime flow; preprocessor selects ABI-specific prototypes.

## State and Persistence
None.

## Dependencies and Integration Points
Ensures `SOLARIS/osi_vm.c`, `osi_vnodeops.c`, and syscall/VFS code agree on signatures for pageout and setgroups interception.

## Risks
Prototype drift can cause kernel ABI mismatches. Solaris 11 and older signatures differ in size types and caller context handling.

## Test Signals
Build all Solaris release targets with warnings for incompatible declarations, especially `afs_putpage` and `afs_xsetgroups`.
