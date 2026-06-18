# sources/distributed-fs/openafs/src/afs/OBSD/osi_machdep.h

## Purpose
OpenBSD OSI machine-dependent compatibility header that maps OpenAFS portable names to OpenBSD kernel types, locks, VFS/vnode fields, allocation, credentials, time, and lookup helpers.

## Important APIs, Types, and Functions
Defines `afs_proc_t`, `afs_ucred_t`, vnode/uio/VFS field macros, `AFS_KALLOC`, `AFS_KFREE`, `BSD_KMALLOC`, `BSD_KFREE`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, `NETPRI`, `USERPRI`, `IsAfsVnode`, `vType`, `vSetVfsp`, `vSetType`, `osi_GetTime`, and prototypes for `afs_obsd_lookupname`, `afs_obsd_getnewvnode`, and `afs_vget`.

## Control Flow
This header is compile-time control flow: OpenBSD release macros select old or new allocation APIs, lock-manager signatures, global-lock implementation, and vnode operation table shape.

## State and Persistence
Declares external global lock state (`afs_global_lock`, sometimes `afs_global_owner`) and references live process and credential state through macros. No persistent data is stored.

## Dependencies and Integration Points
Tightly integrated with OpenBSD kernel headers and with common OpenAFS code included via `afs_osi.h`. It is the contract that lets generic AFS code compile on OpenBSD.

## Risks
Macro indirection can hide side effects, particularly `getpid()` returning `curproc` and `afs_suser(x)` ignoring its argument. Kernel-version drift in lock and VOP APIs can silently break builds. The global owner tracking path asserts ownership manually.

## Test Signals
Compile across supported OpenBSD releases, enable lock diagnostics, exercise memory allocation while GLOCK is held, and validate VFS/vnode macros through mount/root/read/write flows.
