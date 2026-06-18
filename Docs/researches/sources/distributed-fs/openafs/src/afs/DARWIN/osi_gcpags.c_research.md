# sources/distributed-fs/openafs/src/afs/DARWIN/osi_gcpags.c

## Purpose
Supports PAG garbage collection on Darwin by exposing process traversal and process-to-credential conversion when `AFS_GCPAGS` is enabled.

## Important APIs, Types, And Functions
`afs_osi_TraverseProcTable` walks non-system, non-zombie processes on pre-Darwin 8 kernels. `afs_osi_proc2cred` returns a credential snapshot for a process, using `proc_ucred` on Darwin 8+ or `pcred_readlock` on older kernels.

## Control Flow
The traversal callback filters process states and invokes `afs_GCPAGs_perproc_func`. Credential conversion copies uid and group data into a static `afs_ucred_t` on Darwin variants that require a stable OpenAFS credential view.

## State And Persistence
There is no durable state. Darwin 8+ and older implementations use a static credential copy, so returned pointers are overwritten by subsequent calls.

## Dependencies And Integration Points
Depends on Darwin process lists, process credential APIs, OpenAFS PAG scanner code, `PagInCred` consumers, and group-layout conventions.

## Risks
Static credential storage is not reentrant. Process state and credential lifetimes can race with exit or credential mutation, so the code copies only a small credential subset. Darwin 8+ lacks an in-file process table traversal implementation, so external scanner behavior must supply process iteration.

## Test Signals
Enable `AFS_GCPAGS`, create and destroy processes with PAG-bearing credentials, and confirm stale PAGs are reclaimed while live user processes retain tokens. Concurrency tests should look for corrupted group copies or crashes during process exit.
