# sources/distributed-fs/openafs/src/config/param.nbsd60.h

## Purpose
This NetBSD parameter header targets NetBSD 6.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
Source-specific risk: the userland include guard contains `!defined()` with an empty macro name, which is syntactically suspicious and should be compile-tested on the intended preprocessor.
The file is 143 lines and defines 72 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NBSD40_ENV` = `1`
- `AFS_NBSD50_ENV` = `1`
- `AFS_NBSD60_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `RXK_LISTENER_ENV` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Suspicious empty `!defined()` preprocessor condition needs compiler validation.
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
