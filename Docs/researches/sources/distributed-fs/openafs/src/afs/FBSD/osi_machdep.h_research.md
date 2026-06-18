# sources/distributed-fs/openafs/src/afs/FBSD/osi_machdep.h

## Purpose
Defines the FreeBSD OSI machine-dependent adaptation layer for OpenAFS, including vnode/VFS macros, global locking, credentials, privileges, memory allocation hooks, and time helpers.

## Important APIs, Types, And Functions
Key definitions include `osi_Time`, `afs_hz`, `afs_ucred_t`, `afs_proc_t`, vnode type helpers, `IsAfsVnode`, `osi_vinvalbuf`, lookup macro redirects, `afs_osi_Alloc_NoSleep`, `VN_RELE`, `VN_HOLD`, FreeBSD privilege wrappers for `afs_suser`, process/credential macros, `gop_rdwr`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `osi_procname`, and inline `osi_GetTime`.

## Control Flow
The global lock macros assert mutex ownership/non-ownership and lock or unlock `afs_global_mtx`. Privilege macros call `priv_check` for OpenAFS admin and daemon privileges. `osi_GetTime` fetches `microtime`.

## State And Persistence
References persistent globals `afs_global_mtx`, `afs_global_owner`, and pbuf accounting/UMA state. It does not allocate state directly.

## Dependencies And Integration Points
Included via `afs_osi.h` by FreeBSD platform and generic OpenAFS code. Depends on FreeBSD vnode, mutex, privilege, time, thread, and buffer APIs.

## Risks
Macro adaptation must track FreeBSD API changes. `afs_suser` requires both configured privileges, so privilege policy changes affect admin operations. Global-lock assertions are non-recursive and will panic on incorrect nesting.

## Test Signals
Full FreeBSD builds, privilege checks for admin/daemon operations, lock assertion tests, vnode operation dispatch, and cache I/O through `gop_rdwr`.
