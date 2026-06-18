# sources/distributed-fs/openafs/src/sys/setpag.c

## Purpose
`setpag.c` implements `lsetpag`, the local setpag syscall wrapper. The higher-level `setpag` symbol is provided by RMTSYS client logic so it can choose remote or local behavior.

## Important APIs, types, and functions
The exported function is `lsetpag(void)`. Platform implementations call SGI `syscall(AFS_SETPAG)`, Linux `proc_afs_syscall` with fallback to `AFS_SYSCALL`, Darwin/Solaris ioctl glue, or generic `syscall(AFS_SYSCALL, AFSCALL_SETPAG)`.

## Control flow
Conditional compilation selects the local syscall transport. Linux uses proc glue first, then syscall fallback. Darwin and Solaris keep ioctl transport return separate from kernel error value. AIX has no body in the non-AIX block because its calls are linker-exported differently.

## State and persistence behavior
The wrapper itself stores no state. Successful calls create or change the caller's PAG/token namespace in the kernel/cache manager.

## Dependencies and integration points
It depends on `afs_args.h`, platform syscall definitions, `glue.c`, and `afssyscalls.h`. Authentication tools call this through local or RMTSYS paths.

## Risks
Behavior is platform-specific and depends on loaded kernel support. Missing syscall numbers return `-1` without detailed mapping in some builds. PAG creation affects process credential behavior and can interact with setuid flows.

## Test signals
Exercise `lsetpag` on each supported local transport, with and without the AFS kernel module loaded, and verify token isolation after PAG creation.
