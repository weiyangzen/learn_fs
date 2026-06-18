# sources/distributed-fs/openafs/src/afs/DARWIN/osi_module.c

## Purpose
Implements Darwin kext load and unload for OpenAFS, registering the AFS VFS type, vnode operation vectors, syscall or cdev entry points, locks, and devfs node.

## Important APIs, Types, And Functions
`afs_modload` initializes OSI state and registers either `vfs_fsadd` plus `openafs_ioctl` cdev on Darwin 8+ or legacy `vfsconf_add` and syscall table hooks on older kernels. `afs_modunload` unregisters those resources. `KMOD_EXPLICIT_DECL` exposes the kext entry points.

## Control Flow
Modern load initializes mutex infrastructure, creates `afs_global_lock`, registers `afs_vfsentry`, installs cdev switch callbacks, and creates a devfs node. Failures unwind cdev, VFS, mutex, and lock setup. Legacy load registers `afs_vfsconf`, checks syscall availability, and replaces `setgroups` and `AFS_SYSCALL`. Unload refuses while mounted or initialized/shutting down, removes VFS/cdev or restores syscall table entries, and frees locks.

## State And Persistence
Persistent kernel module state includes `afs_vfstable`, cdev major/devfs handle, global lock allocation, legacy `afs_vfsconf`, and modified syscall table entries. The mounted filesystem state `afs_globalVFS` blocks unload.

## Dependencies And Integration Points
Depends on Mach kmod, Darwin VFS registration, devfs/cdev APIs, OpenAFS `osi_Init`, `afs_vfsops`, vnode op descriptors, syscall dispatcher, and group wrapper.

## Risks
Partial load failures must unwind in exact reverse order. Legacy syscall table patching is invasive and must be restored. Unload gating must avoid removing VFS or cdev while active mounts or initialized cache-manager state remain.

## Test Signals
Load/unload kext with no mount, mount then verify unload fails, use `/dev/openafs_ioctl`, verify VFS type appears, and force load-failure paths where cdev or VFS registration is unavailable.
