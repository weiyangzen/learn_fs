# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_machdep.h

## Purpose
Solaris machine-dependent OSI header mapping generic OpenAFS kernel code to Solaris credentials, time, global locking, VFS helpers, large-file checks, and interface structures.

## Important APIs, Types, and Functions
Defines `afs_ucred_t`, `afs_proc_t`, `osi_Time`, `gop_rdwr`, `gop_lookupname`, `afs_suser`, `AFS_GLOCK`, `AFS_GUNLOCK`, `ISAFS_GLOCK`, `osi_InitGlock`, lock flag aliases, `IO_APPEND`, `IO_SYNC`, `AfsLargeFileUio`, `AfsLargeFileSize`, `struct afs_ifinfo`, `osi_procname`, and `osi_GetTime`.

## Control Flow
Compile-time feature macros choose `gethrestime` versus `hrestime`, secpolicy-aware superuser checks, Solaris 10 interface declarations, and 64-bit model support.

## State and Persistence
Declares external `kmutex_t afs_global_lock`, Solaris taskq/interface locks, and reads kernel time/process state. No persistent storage.

## Dependencies and Integration Points
Included through `afs_osi.h` by Solaris platform files and common OpenAFS code. It provides the core GLOCK contract used across Solaris vnode, VFS, file, and VM layers.

## Risks
Large-file macros inspect Solaris-private `uio` fields in non-64-bit clients. `osi_Time` can depend on different kernel time APIs by release. Global-lock macros are simple mutex operations, so callers must not recurse.

## Test Signals
Compile Solaris 9/10/11 variants, verify GLOCK ownership assertions, large-file rejection in 32-bit clients, time retrieval, and NFS translator module path checks.
