## sources/distributed-fs/openafs/src/afs/NBSD/osi_kmod.c

Purpose: modern NetBSD kernel module entry point for OpenAFS. It attaches the AFS VFS and installs syscall hooks for `afs3_syscall`, `setgroups`, and `ioctl`.

Important APIs and state: defines `MODULE(MODULE_CLASS_VFS, openafs, NULL)` and static `openafs_modcmd`. It declares `openafs_sysent` for `AFS_SYSCALL`, saves `old_sysent`, `old_setgroups`, and `old_ioctl`, and references `afs_vfsops`, `afs3_syscall`, `Afs_xsetgroups`, and `afs_xioctl`. `SYS_NOSYSCALL` maps to the right no-module/no-syscall function for NetBSD 7, 6, or older LKM environments.

Control flow: on `MODULE_CMD_INIT`, it selects the syscall table (`sysent` or `emul_netbsd.e_sysent` for RUMP), attaches `afs_vfsops`, saves old syscall handlers, and if the AFS syscall slot is unused (or always in RUMP) patches AFS syscall, `SYS_setgroups`, and `SYS_ioctl`. NetBSD 6+ wraps table mutation in `kernconfig_lock`. If the slot is busy it returns `EBUSY`. On `MODULE_CMD_FINI`, it restores all saved syscall handlers, detaches VFS ops, and returns detach errors. NetBSD 7 autounload returns `EBUSY`.

Dependencies and integration: depends on NetBSD module, syscall, VFS, and optional RUMP APIs. It integrates the NetBSD files in this subset: `osi_groups.c` provides `Afs_xsetgroups`, `osi_vfsops.c` provides `afs_vfsops`, and common AFS code provides syscall/ioctl handlers.

State and persistence: mutates live kernel syscall table and VFS registry only during module lifetime. No disk persistence.

Risks: partial initialization failure after `vfs_attach` but before syscall patching may need careful unwind; the inspected code breaks with error but does not visibly detach in the busy-slot branch. Syscall table patching must be restored exactly on fini. Autounload refusal prevents unsafe unload while mounted or hooked.

Test signals: module load/unload, busy `AFS_SYSCALL` slot, RUMP module load, NetBSD 6+ kernconfig locking builds, VFS attach/detach, syscall/ioctl routing, and failed-init cleanup behavior.
