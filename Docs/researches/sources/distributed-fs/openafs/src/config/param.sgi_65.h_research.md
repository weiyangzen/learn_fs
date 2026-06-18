# sources/distributed-fs/openafs/src/config/param.sgi_65.h

## Purpose
This IRIX 6.5 parameter header declares SGI VFS/VFS include behavior, SGI 6.5 and extent-magic support, flock sysid support, rx listener, 64-bit client and pointer markers, ffs/statvfs support, global locking, SGI private syscall offsets, XFS inode-operation support, big-endian identity, and VM read/write support.
The kernel branch sets ABI helpers, VFS/uio/sysv-lock mappings, kmem allocation, `AFS_EVENT_LOCK`, and optional memory-function compatibility macros. The UKERNEL branch provides SGI userspace markers, AFS syscall values, userspace IP/rx settings, uio aliases, `AFS_DIRENT`, `CMSERVERPREF`, and `ROOTINO`.
The file is 173 lines and defines 92 preprocessor symbols. Its `SYS_NAME` is `"sgi_65"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sgi_65`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_HH` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_SGI_ENV` = `1`
- `AFS_SGI65_ENV` = `1`
- `AFS_SGI_EXMAG` = `1	/* use magic fields in extents for AFS extra fields */`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `RXK_LISTENER_ENV` = `1	/* Use an rx listener daemon */`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BITPOINTER_ENV` = `1	/* pointers are 64 bits. */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_PIOCTL` = `64+1000`
- `AFS_SETPAG` = `65+1000`
- `AFS_IOPEN` = `66+1000`
- `AFS_ICREATE` = `67+1000`
- `AFS_IREAD` = `68+1000`
- `AFS_IWRITE` = `69+1000`
- `AFS_IINC` = `70+1000`
- `AFS_IDEC` = `71+1000`
- `AFS_IOPEN64` = `72+1000	/* was never-used aux call. */`
- `AFS_SYSCALL` = `73+1000`
- `AFS_SGI_XFS_IOPS_ENV` = `1	/* turns on XFS inode ops. */`
- `AFS_64BIT_IOPS_ENV` = `1	/* inode ops expect 64 bit inodes */`
- `sys_sgi_65` = `1`
- `SYS_NAME` = `"sgi_65"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sgi_65`
- `AFSBIG_ENDIAN` = `1`
- `AFS_VM_RDWR_ENV` = `1`
- `AFS_VFS34` = `1	/* afs/afs_vfsops.c (afs_vget), afs/afs_vnodeops.c (afs_lockctl, afs_noop) */`
- `AFS_UIOFMODE` = `1	/* Only in afs/afs_vnodeops.c (afs_ustrategy) */`
- `AFS_SYSVLOCK` = `1	/* sys v locking supported */`

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

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
- Pointer-width macros must match the compiler ABI or ioctl/kernel-user structures can be mis-sized.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
