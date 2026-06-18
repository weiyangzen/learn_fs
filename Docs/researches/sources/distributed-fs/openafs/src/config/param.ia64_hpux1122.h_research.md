# sources/distributed-fs/openafs/src/config/param.ia64_hpux1122.h

## Purpose
This IA-64 HP-UX header targets HP-UX 1122. It accumulates HP-UX release macros through 11.22/11.23, enables 64-bit client behavior and LP64 pointer markers when `__LP64__` is present, declares syscall slot 48, big-endian identity, statvfs/ffs support, rx listener, userspace IP address handling, global AFS locking, and gettimeofday-based rx clock behavior.
The `KERNEL` branch maps OpenAFS uio, allocation, and vnode-attribute abstraction names onto HP-UX kernel names, sets `_KERNEL`, declares `AFS_HPUX_64BIT_ENV` for LP64, and for non-UKERNEL kernel builds maps memset/memcpy/memcmp to bzero/bcopy/bcmp.
The header defines `EDQUOT` if missing and forces `USE_UCONTEXT`, so build tests must cover both HP-UX system headers and user context availability.
The file is 102 lines and defines 47 preprocessor symbols. Its `SYS_NAME` is `"ia64_hpux1122"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ia64_hpux1122`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_HPUX_ENV` = `1`
- `AFS_HPUX90_ENV` = `1`
- `AFS_HPUX100_ENV` = `1`
- `AFS_HPUX101_ENV` = `1`
- `AFS_HPUX102_ENV` = `1`
- `AFS_HPUX110_ENV` = `1`
- `AFS_HPUX1111_ENV` = `1`
- `AFS_HPUX1122_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BITPOINTER_ENV` = `1	/* pointers are 64 bits. */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_SYSCALL` = `48	/* slot reserved for AFS */`
- `SYS_NAME` = `"ia64_hpux1122"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ia64_hpux1122`
- `AFSBIG_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_VOID_PTR` = `1`
- `AFS_TEXT_ENV` = `1	/* Older kernels use TEXT */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `NEARINODE_HINT` = `1	/* hint to ufs module to scatter inodes on disk */`
- `AFS_UIOSYS` = `UIOSEG_KERNEL`
- `AFS_UIOUSER` = `UIOSEG_USER`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_MINCHANGE` = `2`
- `AFS_KALLOC` = `kmem_alloc`
- `AFS_KFREE` = `kmem_free`
- `AFS_HPUX_64BIT_ENV` = `1`
- `AFS_DIRENT` = ``
- `USE_UCONTEXT` = `/* should be in afsconfig.h */`

Additional API/type notes:
- macro function `nearInodeHash(volid, hval)` for NAMEI inode placement

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `__LP64__` selects 64-bit pointer behavior

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Pointer-width macros must match the compiler ABI or ioctl/kernel-user structures can be mis-sized.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Kernel structure field aliases are tightly coupled to OS header versions.
- NAMEI cache inode placement changes can affect cache distribution and upgrade behavior.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
