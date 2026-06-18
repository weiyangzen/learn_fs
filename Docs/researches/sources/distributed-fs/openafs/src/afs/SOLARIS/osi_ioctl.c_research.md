# sources/distributed-fs/openafs/src/afs/SOLARIS/osi_ioctl.c

## Purpose
Solaris 11 `/dev/afs` ioctl emulation for the older AFS syscall interface.

## Important APIs, Types, and Functions
Under `AFS_SUN511_ENV`, defines character-device callbacks `devafs_open`, `devafs_close`, `devafs_ioctl`, `devafs_getinfo`, `devafs_attach`, `devafs_detach`, `afs_devops`, and `afs_modldrv`.

## Control Flow
Open/close validate minor number and character-device open type. Ioctl accepts `VIOC_SYSCALL` and `VIOC_SYSCALL32`, copies user args with `ddi_copyin`, maps them into `struct afssysa`, calls `Afs_syscall`, and returns either syscall error or `rv.r_val1`. Attach creates the minor node `afs`; detach removes properties and the minor node.

## State and Persistence
Global `devafs_dip` tracks the attached device instance. No persistent data is stored.

## Dependencies and Integration Points
Depends on Solaris DDI/DDK character device APIs and `Afs_syscall`. Integrated into module linkage from `SOLARIS/osi_vfsops.c` for Solaris 11.

## Risks
Only a single minor is supported. Return-value mapping treats successful `Afs_syscall` rval as an error code for ioctl callers. Copyin mode and 32/64-bit struct layouts must match userland.

## Test Signals
Solaris 11 attach creates `/dev/afs`, invalid minors fail, both 32-bit and native ioctl paths dispatch to AFS syscall, and detach removes the minor without leaving `devafs_dip` stale.
