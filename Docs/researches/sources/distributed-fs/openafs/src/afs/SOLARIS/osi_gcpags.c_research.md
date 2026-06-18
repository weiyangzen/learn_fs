# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_gcpags.c

## Purpose
Solaris PAG garbage-collection support: traverse active processes and expose process credentials.

## Important APIs, Types, and Functions
Defines `afs_osi_TraverseProcTable` and `afs_osi_proc2cred` under `AFS_GCPAGS`.

## Control Flow
Traversal iterates `practive` via `p_next` and calls `afs_GCPAGs_perproc_func` for each process. Credential lookup returns `pr->p_cred` or `NULL`.

## State and Persistence
No owned state. Reads live process table and credential pointers.

## Dependencies and Integration Points
Depends on Solaris process-list globals and OpenAFS common PAG GC callback. Used to identify PAGs no longer referenced by active processes.

## Risks
Traversal has implicit process table locking assumptions not visible in this file. Returned credentials are borrowed pointers. Process-list APIs are historically unstable.

## Test Signals
Build with `AFS_GCPAGS`, run PAG GC under process churn, verify null handling, and ensure traversal does not race or panic on active-process list changes.
