# sources/distributed-fs/openafs/src/sys/sys_prototypes.h

## Purpose
`sys_prototypes.h` centralizes prototypes for syscall glue, local pioctl/setpag wrappers, RMTSYS client/server functions, and conversion helpers in `src/sys`.

## Important APIs, types, and functions
It declares platform glue (`proc_afs_syscall`, `ioctl_afs_syscall`, `ioctl_sun_afs_syscall`), `lpioctl`, RMTSYS client `pioctl`/`setpag`, conversion functions `inparam_conversion`/`outparam_conversion`, server helpers `rmt_Quit`/`rmtsysd`, and `lsetpag`.

## Control flow
There is no runtime control flow. Preprocessor conditionals expose only platform-relevant glue prototypes.

## State and persistence behavior
No state is stored here; it defines cross-file interfaces for stateful syscall/RPC operations.

## Dependencies and integration points
It depends on OpenAFS integer types and `struct ViceIoctl`. It ties together `glue.c`, `pioctl.c`, `rmtsysc.c`, `rmtsysnet.c`, `rmtsyss.c`, and `setpag.c`.

## Risks
Prototype drift from implementation signatures can cause subtle ABI bugs, especially for pointer-sized Solaris/Darwin parameters. Broad declarations of `setpag`/`pioctl` can collide with platform/library names.

## Test signals
Compile `src/sys` with strict prototype warnings on Linux, Darwin, Solaris, and generic Unix configurations.
