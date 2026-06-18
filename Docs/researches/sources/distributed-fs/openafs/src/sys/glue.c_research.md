# sources/distributed-fs/openafs/src/sys/glue.c

## Purpose
`glue.c` supplies C-level platform glue for invoking OpenAFS kernel syscalls through proc/ioctl mechanisms when a direct syscall stub is not sufficient.

## Important APIs, types, and functions
Platform exports are `proc_afs_syscall` for Linux, `ioctl_afs_syscall` for Darwin 8+ with optional 64-bit Darwin handling, and `ioctl_sun_afs_syscall` for Solaris 11. Each accepts an OpenAFS syscall opcode, up to six parameters where supported, and returns an ioctl/syscall result separately from the kernel-returned error.

## Control flow
Linux opens `/proc` syscall files, fills `struct afsprocdata`, and issues `VIOC_SYSCALL`. Darwin opens `SYSCALL_DEV_FNAME`, selects `VIOC_SYSCALL` or `VIOC_SYSCALL64`, performs ioctl, and extracts the returned value. Solaris chooses a 32-bit or native argument struct, opens `SYSCALL_DEV_FNAME`, and issues the appropriate ioctl.

## State and persistence behavior
No durable state is stored. The functions open device/proc files, call into the loaded AFS kernel module, and close the descriptors.

## Dependencies and integration points
It depends on `afs_args.h`, `sys_prototypes.h`, syscall device path macros, and platform kernel-module ioctl ABIs. `setpag.c` and `pioctl.c` call these functions as fallback or primary local syscall transport.

## Risks
ABI struct mismatches break all local pioctl/setpag operations for a platform. Linux fallback behavior depends on both OpenAFS and Arla proc names. Darwin's pointer-size branch is compile/runtime sensitive, and Solaris must match ILP32/native ioctl numbers.

## Test signals
Exercise `lsetpag` and `lpioctl` on Linux with proc syscall available and absent, Darwin 32/64-bit builds, and Solaris ILP32/native builds. Verify file descriptors close on both success and failure.
