# sources/distributed-fs/openafs/src/afs/DFBSD/osi_gcpags.c

## Purpose
Provides DragonFly BSD PAG garbage-collection credential access when `AFS_GCPAGS` is enabled.

## Important APIs, Types, And Functions
`afs_osi_proc2cred(afs_proc_t *pr)` returns `pr->p_cred` for a process, or `NULL` for a null process pointer.

## Control Flow
The function performs a null check and directly exposes the process credential pointer; there is no process traversal implementation in this file.

## State And Persistence
No local state is stored. Returned credential state belongs to the process.

## Dependencies And Integration Points
Depends on DragonFly process credential layout and OpenAFS PAG scanner code that consumes process credentials.

## Risks
Returning a live credential pointer means lifetime and locking must be valid in the caller. Unlike Darwin/FreeBSD snapshots, this path does not copy credentials or filter process states.

## Test Signals
Enable PAG GC and verify process credentials can be inspected without crashes during token cleanup, including process-exit races.
