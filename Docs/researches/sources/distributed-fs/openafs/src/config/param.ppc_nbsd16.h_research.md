# sources/distributed-fs/openafs/src/config/param.ppc_nbsd16.h

## Purpose
This NetBSD parameter header targets NetBSD 1.6. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 78 lines and defines 37 preprocessor symbols. Its `SYS_NAME` is `"i386_nbsd16"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_nbsd16`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `SYS_NAME` = `"macppc_nbsd16"`
- `SYS_NAME_ID` = `SYS_NAME_ID_macppc_nbsd16`
- `AFS_PPC_ENV` = `1`
- `AFSBIG_ENDIAN` = `1`
- `AFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_KERBEROS_ENV` = ``
- `AFS_SYSCALL` = `210`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `0	/* System doesn't support statvfs */`
- `AFS_UIOSYS` = `1`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `MCLBYTES`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
