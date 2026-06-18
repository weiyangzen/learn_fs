# sources/distributed-fs/openafs/src/afs/DARWIN/osi_machdep.h

## Purpose
Defines the Darwin OS-interface layer that adapts generic OpenAFS kernel code to Darwin process, credential, vnode, VFS, lock, uio, time, and cache APIs.

## Important APIs, Types, And Functions
Important definitions include `vop_cred`, `vop_proc`, `cn_cred`, vnode and VFS compatibility macros, `afs_ucred_t`, `afs_proc_t`, `VN_HOLD`, `VN_RELE`, `gop_rdwr`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, cache filesystem type constants, `osi_curproc`, `osi_curcred`, `afsio_*` wrappers, `IsAfsVnode`, `vSetType`, `osi_procname`, and inline `osi_GetTime`.

## Control Flow
Most entries are macros that change how generic code compiles. Modern Darwin maps credential and vnode operations to KPI functions such as `kauth_cred_*`, `vnode_*`, `vfs_*`, and `ubc_msync`. Global lock macros assert non-recursive ownership by the current thread, acquire/release a Darwin lock, and maintain `afs_global_owner`.

## State And Persistence
The header references global lock state (`afs_global_lock`, `afs_global_owner`), VFS typenum, `afs_osi_ctxtp`, feature toggles (`afs_darwin_realmodes`, `afs_darwin_fsevents`), and cache filesystem identity. It does not allocate state directly.

## Dependencies And Integration Points
This header is pulled in through `afs_osi.h` and is foundational for all Darwin files in this group. It bridges OpenAFS to Darwin KPI, legacy BSD kernel APIs, UBC, and KAUTH credentials.

## Risks
Macro-level ABI adaptation is brittle: wrong version guards can silently compile code against the wrong vnode/credential semantics. The global lock assertions assume no recursive entry. `osi_curcred` maps to `afs_osi_credp`, which is not always the current user credential.

## Test Signals
Successful builds across supported Darwin version macros, lock assertion coverage, vnode type/mount detection, credential ref/unref paths, and mount/root/vnode operations all validate this header.
