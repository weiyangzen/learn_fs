# sources/distributed-fs/openafs/src/sys/pioctl.c

## Purpose
`pioctl.c` implements `lpioctl`, the local pioctl syscall wrapper. Remote dispatch is handled elsewhere by `rmtsysc.c`; this file exists separately so small shared libraries can include only the local pioctl entry point.

## Important APIs, types, and functions
The exported function is `lpioctl(char *path, int cmd, void *cmarg, int follow)`. Platform-specific paths use direct `syscall(AFS_PIOCTL)` on SGI, Linux `proc_afs_syscall` with fallback to `AFS_SYSCALL`, Darwin `ioctl_afs_syscall`, Solaris `ioctl_sun_afs_syscall`, or generic `syscall(AFS_SYSCALL, AFSCALL_PIOCTL, ...)`.

## Control flow
The Linux path first attempts `/proc` ioctl glue and falls back to the AFS syscall number if available. The generic path ignores `SIGSYS` around the syscall so missing kernel support does not kill the process, restoring the handler afterward. Darwin/Solaris keep ioctl return status and kernel error status distinct.

## State and persistence behavior
The wrapper itself stores no state but forwards pioctl requests that may read or mutate cache-manager state, tokens, mountpoints, ACLs, cells, or cache configuration.

## Dependencies and integration points
It depends on `afs_args.h`, `afssyscalls.h`, `sys_prototypes.h`, and platform glue in `glue.c`. User tools such as `fs`, token utilities, and RMTSYS server code depend on this local entry point.

## Risks
Signal-handler manipulation is process-global and not thread-safe. Platform return conventions differ, so error precedence can regress. `void *cmarg` must match `struct ViceIoctl` expectations for the kernel opcode.

## Test signals
Exercise representative pioctls through `lpioctl` on Linux proc and syscall fallback, Darwin, Solaris, SGI, and a system without loaded AFS support to confirm graceful errors.
