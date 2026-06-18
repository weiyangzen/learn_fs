# sources/distributed-fs/openafs/src/afs/LINUX/osi_prototypes.h

## Purpose
This Linux header declares platform OSI functions exported across the OpenAFS Linux kernel implementation. It is the shared prototype surface for allocator, credential, NFS translator, file, ioctl, misc, syscall probe, proc, sleep, sysctl, VM, vcache, vfs, vnode, and groups/keyring code.

## Important APIs, types, and functions
The header declares:
- Allocator APIs: `osi_linux_alloc`, `osi_linux_free`, `osi_linux_free_afs_memory`, `osi_linux_verify_alloced_memory`.
- Credential APIs: `crget`, `crfree`, `crdup`, `crref`, `crset`.
- NFS translator APIs and `afs_xnfssrv`.
- Cache file APIs: `osi_InitCacheInfo`, `osi_rdwr`, `afs_linux_raw_open`.
- Proc/ioctl/syscall/sysctl lifecycle APIs.
- VM and vcache helpers for flushing, smushing, storing, and resetting root vcache.
- VFS/vnode helpers: `vattr2inode`, inode cache lifecycle, `afs_fill_inode`.
- PAG/keyring APIs: `osi_keyring_init`, `osi_keyring_shutdown`, `__setpag`, optional `osi_get_keyring_pag`, and `key_type_afs_pag`.

## Control flow and behavior
There is no executable control flow. The header coordinates C compilation by making cross-file symbols visible.

## State and persistence
No state is owned here. It declares external state such as `afs_xnfssrv` and `key_type_afs_pag`.

## Dependencies and integration points
This is a central integration header for Linux OpenAFS platform files. It assumes many OpenAFS types are already declared (`struct vrequest`, `afs_ucred_t`, `struct osi_file`, `struct vcache`, etc.) and is included by code needing cross-module prototypes.

## Risks
Prototype drift is the main risk. If function signatures in implementation files change without updating this header, old-style implicit declarations or ABI mismatches can appear depending on compiler settings. Conditional keyring prototypes must match `LINUX_KEYRING_SUPPORT`.

## Test signals
Compiler warnings/errors for missing or incompatible prototypes are the primary signal. Full Linux module builds with keyring and non-keyring configs verify the conditional declarations.
