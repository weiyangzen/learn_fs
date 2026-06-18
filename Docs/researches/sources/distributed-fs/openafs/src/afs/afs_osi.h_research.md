# sources/distributed-fs/openafs/src/afs/afs_osi.h

## Purpose
`afs_osi.h` is the common OSI contract header for AFS kernel code. It defines portable types, file/device/socket abstractions, vnode/vcache hooks, global lock and copy wrappers, UIO access macros, PAG group layout constants, and default vnode/refcount behavior that platform-specific `osi_machdep.h` can override.

## Important APIs, types, and macros
Important types include `struct osi_socket`, `struct osi_stat`, `struct osi_file`, `struct osi_dev`, `struct afs_osi_WaitHandle`, and fixed-size `osi_timeval32_t`. File macros include `osi_SetFileProc`, `osi_SetFileRock`, `osi_GetFileProc`, and `osi_GetFileRock`. Vnode hooks include `osi_TryEvictVCache`, `osi_NewVnode`, `osi_PrePopulateVCache`, `osi_PostPopulateVCache`, `osi_AttachVnode`, `osi_ResetVCache`, and `osi_vnhold`.

The header defines `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `RX_AFS_GLOCK`, `AFS_RELE`, `AFS_FAST_RELE`, `AFS_COPYIN`, `AFS_COPYINSTR`, `AFS_COPYOUT`, `AFS_UIOMOVE`, `AFS_UIO_OFFSET`, `AFS_UIO_RESID`, `AFS_UIO_SETOFFSET`, `AFS_UIO_SETRESID`, and default vnode/vfs argument conversion macros.

## Control flow and contracts
The most important behavioral contract is that user/kernel copy and UIO moves may drop the AFS global lock before operations that can fault or block, then reacquire it. This is conditional on `AFS_GLOBAL_SUNLOCK`. UIO signatures are normalized across Darwin, BSD, and older Unix variants. Vnode reference macros wrap platform `VN_RELE` and deliberately drop the global lock for non-UKERNEL builds.

Platform-specific behavior is layered by defining defaults first, then including `osi_machdep.h`, allowing the platform header to redefine vnode types, global lock behavior, UIO details, and credential access.

## State and persistence behavior
The header itself stores no state, but its structures define runtime state shapes used throughout the Cache Manager. `struct osi_file` begins with `size` and stores platform file/vnode handles, offset, optional write callback, rock pointer, and UKERNEL fd. `struct osi_dev` stores platform-specific device or mount identity.

## Dependencies and integration points
Every source in this subset includes or indirectly depends on this header. It integrates kernel headers, Linux dummy inode-info shields, Coda/XFS include conflict avoidance, vnode operations, credential globals, PAG group count, and optional Linux delayed remove/unlink behavior.

## Risks and edge cases
Because this header normalizes many kernel ABIs, macro mistakes have broad blast radius. Copy/Uiomove wrappers must not leave the global lock in the wrong state. Darwin user-address casting is version-gated to avoid 32/64-bit userspace issues. `AFS_FAST_RELE` intentionally bypasses full inactive behavior on some platforms and must only be used under its assumptions.

## Test signals
Build coverage across Linux, Solaris, Darwin, BSD, AIX, and UKERNEL is the primary signal. Runtime signals include copyin/copyout while holding/not holding the global lock, UIO moves on Darwin and BSD variants, vnode release behavior, `osi_vnhold` failure handling, and PAG group count behavior under one-group and two-group builds.
