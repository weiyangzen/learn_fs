# sources/distributed-fs/openafs/src/afs/LINUX/osi_cred.c

## Purpose
This file provides Linux credential allocation, duplication, reference, and installation routines for OpenAFS kernel code. It abstracts older in-task credential fields and newer `struct cred` reference semantics behind the AFS `cred_t` interface.

## Important APIs, types, and functions
- `crget()` allocates a credential object and initializes its reference state.
- `crfree(cr)` releases a credential and associated group-info references.
- `crdup(cr)` returns an independent duplicate credential.
- `crref()` returns a reference/snapshot of the current task credentials.
- `crset(cr)` installs credential values into the current task.
- `afs_copy_creds(to, from)` copies uid/gid/fsuid/fsgid and group info while maintaining group reference counts.

## Control flow and behavior
On kernels with `STRUCT_TASK_STRUCT_HAS_CRED`, `crref` uses `get_current_cred`, `crfree` uses `put_cred`, and `crset` creates mutable credentials with `prepare_creds`, replaces group info, and commits them with `commit_creds` only if `current->cred == current->real_cred`. Older kernels allocate/free raw `cred_t` with `kmalloc`/`kfree`, maintain `cr_ref`, copy uid/gid fields directly, and update `current` fields under `task_lock` when group info changes.

## State and persistence
Credentials are in-memory kernel objects with reference counts and group-info ownership. There is no disk persistence. `crset` mutates the current task credential state, affecting later permission checks and PAG/group behavior.

## Dependencies and integration points
This layer is used by Linux PAG/keyring, NFS translator, ioctl/syscall, cache I/O, and export code whenever an AFS request needs caller credentials. It depends on OpenAFS credential macros (`afs_cr_uid`, `afs_set_cr_group_info`, etc.) and Linux group-info reference APIs.

## Risks
`crget` on modern credential kernels calls `get_cred(tmp)` on freshly allocated memory, which relies on `cred_t` layout/configuration assumptions elsewhere in the tree; this is a sensitive area for kernel API drift. `crset` silently returns when real and effective credentials differ, which can surprise callers expecting a credential change. Group-info reference ownership must stay exact or leaks/use-after-free bugs follow. Older branches directly mutate `current` credential fields, which is unsafe on newer kernels and must be gated correctly.

## Test signals
Build tests across both credential models are essential. Runtime tests should cover `setpag`, `setgroups`, token lookup under duplicated credentials, `crset` for matching/nonmatching real credentials, group reference leak detection, and NFS translator/export request credential propagation.
