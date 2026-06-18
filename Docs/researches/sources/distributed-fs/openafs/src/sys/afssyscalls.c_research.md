# sources/distributed-fs/openafs/src/sys/afssyscalls.c

## Purpose
`afssyscalls.c` provides user-space wrappers around OpenAFS inode-related kernel calls and helper routines for reading, writing, and printing AFS vice inodes. It is compiled into the sys libraries used by server and utility code on non-namei configurations.

## Important APIs, types, and functions
Exported routines include `icreate`, `iopen`, `iinc`, `idec`, SGI XFS variants `icreatename64`, `iopen64`, `iinc64`, `idec64`, `ilistinode64`, optional `afs_init_kernel_config`, `inode_read`, `inode_write`, and `PrintInode`. Debug builds add `debug_icreatename64`, `debug_iopen64`, `debug_iinc64`, `debug_idec64`, and internal `check_iops`.

## Control flow
Platform conditionals select direct AFS syscall numbers on SGI, a shared `AFS_SYSCALL` entry with `AFSCALL_*` operation numbers elsewhere, or no code on AIX where system calls look like normal calls. Some calls pack parameters into `struct iparam` to fit syscall argument limits. `inode_read`/`inode_write` open an inode through `IOPEN`, seek, transfer bytes, close, and return the byte count or `-1`.

## State and persistence behavior
The wrappers mutate kernel AFS inode state through create/open/increment/decrement calls and ordinary file reads/writes after `IOPEN`. In debug builds, global arrays remember file/line call sites already logged to `inode_debug_log`.

## Dependencies and integration points
The file depends on `afs_args.h`, `afssyscalls.h`, platform syscall numbers, SGI XFS attribute support, and AFS inode macro selection. It underpins utilities in `src/sys`, salvager/fileserver inode code, and compatibility with legacy inode-based partition storage.

## Risks
The code is heavily controlled by platform macros; untested platform combinations can silently compile the wrong syscall path. Debug `realloc(*iops, ...)` is suspicious because `*iops` is an element, not the pointer variable, making debug-only allocation fragile. `inode_read` and `inode_write` compare `lseek` results against an unsigned offset via `int code`, which can be wrong for large offsets.

## Test signals
Build with and without `AFS_NAMEI_ENV`, with `AFS_64BIT_IOPS_ENV`, and for SGI XFS if supported. Runtime tests should exercise `ICREATE`, `IOPEN`, `IINC`, `IDEC`, `inode_read`, `inode_write`, and debug logging on a controlled vice partition.
