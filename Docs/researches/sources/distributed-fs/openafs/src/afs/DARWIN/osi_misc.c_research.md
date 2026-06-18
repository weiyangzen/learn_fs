# sources/distributed-fs/openafs/src/afs/DARWIN/osi_misc.c

## Purpose
Collects Darwin miscellaneous OS glue: pathname lookup, superuser checks, partial uio copying, reusable VFS context handling, fsevent permission notifications, and the character-device ioctl bridge for modern Darwin.

## Important APIs, Types, And Functions
`darwin_notify_perms` synthesizes permission-change notifications for directory vnodes. `osi_lookupname_user` and `osi_lookupname` resolve paths. `afs_suser` tests superuser privilege. `afsio_partialcopy` builds a bounded duplicate uio. `get_vfs_context` and `put_vfs_context` manage `afs_osi_ctxtp`. `afs_cdev_nop_openclose` and `afs_cdev_ioctl` expose syscall forwarding through `/dev/openafs_ioctl`.

## Control Flow
Permission notification walks the vcache hash under the AFS global lock, skips dead, non-directory, dynroot, mount-point, or reclaiming vnodes, obtains vnode refs, marks `CEvent`, drops the lock, calls `vnode_setattr`, then resumes scanning. Lookup uses `vnode_lookup` with optional no-follow on modern Darwin and `namei` on older kernels. VFS-context acquisition serializes reuse by process/thread and sleeps if another owner is active. The cdev ioctl validates 32/64-bit ioctl command shape, calls `afs3_syscall`, and writes the return value into the user ABI structure.

## State And Persistence
Persistent globals are `afs_osi_ctxtp`, `afs_osi_ctxtp_initialized`, `vfs_context_owner`, `vfs_context_curproc`, and `vfs_context_ref`. `darwin_notify_perms` temporarily mutates vcache `CEvent`.

## Dependencies And Integration Points
Depends on Darwin VFS context, vnode lookup/setattr, proc bitness APIs, devfs cdev registration from `osi_module.c`, OpenAFS vcache hash tables, token events, and syscall dispatcher `afs3_syscall`.

## Risks
The vcache scan releases and reacquires locks while walking mutable lists, so reference discipline is critical. VFS context ownership can deadlock if put/get imbalance occurs. The ioctl ABI must match both 32-bit and 64-bit user structures. Fake fsevents intentionally mask some internal activity and can confuse permission observers if overused.

## Test Signals
Test path lookup with follow/no-follow, cdev syscall forwarding from 32/64-bit tools, token obtain/discard fsevent behavior, concurrent VFS context use, and shutdown with no leaked context references.
