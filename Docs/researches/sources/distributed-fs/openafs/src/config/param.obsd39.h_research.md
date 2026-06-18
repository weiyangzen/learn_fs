# sources/distributed-fs/openafs/src/config/param.obsd39.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.9. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
This common OpenBSD header also carries a `SYS_NAME`/`SYS_NAME_ID` identity, which is unusual because most OpenBSD common files leave architecture identity to the `param.i386_obsd*.h` overlay.
The file is 61 lines and defines 26 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd39"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd39`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd39"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd39`
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
