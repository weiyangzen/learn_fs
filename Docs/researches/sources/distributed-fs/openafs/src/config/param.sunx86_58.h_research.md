# sources/distributed-fs/openafs/src/config/param.sunx86_58.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 58 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 165 lines and defines 85 preprocessor symbols. Its `SYS_NAME` is `"sunx86_58"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sunx86_58`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_SYSCALL` = `65`
- `sys_sunx86_58` = `1`
- `SYS_NAME` = `"sunx86_58"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sunx86_58`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_VXFS` = `1	/* Support cache on Veritas vxfs file system */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `AFS_HAVE_STATVFS64` = `1	/* System supports statvfs64 */`
- `AFS_VM_RDWR_ENV` = `1	/* read/write implemented via VM */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `NEARINODE_HINT` = `1	/* hint to ufs module to scatter inodes on disk */`
- `AFS_UIOFMODE` = `1	/* Only in afs/afs_vnodeops.c (afs_ustrategy) */`
- `AFS_SYSVLOCK` = `1	/* sys v locking supported */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `MCLBYTES`
- `AFS_MINCHANGE` = `2`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`
- `AFS_DIRENT` = ``

Additional API/type notes:
- macro function `nearInodeHash(volid, hval)` for NAMEI inode placement

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Kernel structure field aliases are tightly coupled to OS header versions.
- NAMEI cache inode placement changes can affect cache distribution and upgrade behavior.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
