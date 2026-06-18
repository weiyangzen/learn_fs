# sources/distributed-fs/openafs/src/afs/UKERNEL/osi_gcpags.c

## Purpose

`osi_gcpags.c` supplies the UKERNEL implementation of process-to-credential lookup for PAG garbage collection when `AFS_GCPAGS` is enabled.

## Important APIs, Types, and Functions

`afs_osi_proc2cred(afs_proc_t *pr)` returns `pr->p_cred` for a non-null process and `NULL` otherwise. Under UKERNEL, `afs_proc_t` is a preprocessor alias to `struct usr_proc`.

## Control Flow

The function is a direct accessor guarded by `#if AFS_GCPAGS`; there is no allocation, locking, or credential copy.

## State and Persistence Behavior

It returns a pointer to process-owned credential state. The caller must treat the returned credential as borrowed and non-persistent. No state is modified.

## Dependencies and Integration Points

It includes the standard UKERNEL headers and `afs/afs_stats.h`. It is used by PAG cleanup code that needs to inspect process credentials without kernel-native process structures.

## Risks and Edge Cases

The function assumes `p_cred` exists in the UKERNEL process type; other code in `sysincludes.h` defines `struct usr_proc` with `p_ucred`, while this file references `p_cred`, making platform macro compatibility worth checking. There is no refcount increment, so callers must not hold the pointer beyond process lifetime.

## Test Signals

Build with `AFS_GCPAGS` enabled for UKERNEL. Runtime tests should create a `usr_proc` with credentials and ensure PAG cleanup sees the expected pointer without leaking or dereferencing null processes.
