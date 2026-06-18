# sources/distributed-fs/openafs/src/sys/afssyscalls.h

## Purpose
`afssyscalls.h` declares the OpenAFS syscall shim API and defines the `Inode` type and convenience macros used by inode-based server utilities.

## Important APIs, types, and functions
It defines `Inode`, `afs_ino_str_t`, `AFS_INO_STR_LENGTH`, `VALID_INO`, `AFS_DEBUG_IOPS_LOG`, and macros `ICREATE`, `IDEC`, `IINC`, and `IOPEN`. It declares SGI XFS 64-bit inode operations, `inode_read`, `inode_write`, `PrintInode`, optional `proc_afs_syscall`, `afs_init_kernel_config`, and local syscall wrappers `lsetpag`/`lpioctl`.

## Control flow
There is no runtime control flow, but preprocessor flow selects inode width and macro targets based on `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_SGI_XFS_IOPS_ENV`, and `AFS_DEBUG_IOPS`.

## State and persistence behavior
The header exposes debug log state via `inode_debug_log` in debug builds. Otherwise it defines only compile-time interfaces to kernel-backed inode state.

## Dependencies and integration points
It includes `afs/param.h` and is consumed by syscall wrappers, server inode code, and test utilities. AIX also gets a broad `int syscall()` declaration because OpenAFS exports a syscall-like function with variable arguments.

## Risks
Macro indirection hides whether callers are invoking 32-bit, 64-bit, debug, or SGI XFS paths. The non-64-bit declarations for `inode_read`/`inode_write` are old-style and lose type checking. AIX's generic `syscall()` prototype is intentionally imprecise.

## Test signals
Compile representative consumers under strict warnings for namei/non-namei, 32-bit/64-bit inode, debug IOPS, SGI XFS, Linux, and AIX configurations.
