# sources/distributed-fs/openafs/src/afs/OBSD/osi_gcpags.c

## Purpose
OpenBSD support for garbage-collecting PAGs by mapping processes to credentials when `AFS_GCPAGS` is enabled.

## Important APIs, Types, and Functions
Defines `afs_osi_proc2cred(afs_proc_t *pr)` under `#if AFS_GCPAGS`. It returns `pr->p_cred` or `NULL`.

## Control Flow
The function guards null process pointers and otherwise returns the process credential pointer directly. There is no process traversal in this file.

## State and Persistence
No state is owned here. It exposes live OpenBSD process credential state to common PAG GC code.

## Dependencies and Integration Points
Depends on OpenBSD `struct proc` layout as aliased by `afs_proc_t`, and OpenAFS PAG GC code that calls `afs_osi_proc2cred`.

## Risks
Returned credentials are borrowed live kernel pointers with no explicit refcounting here. Process or credential lifetime assumptions must be supplied by the traversal caller.

## Test Signals
Build with and without `AFS_GCPAGS`. PAG GC tests should confirm null process handling and correct credential visibility for live processes.
