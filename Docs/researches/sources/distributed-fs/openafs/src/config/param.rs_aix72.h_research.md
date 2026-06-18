# sources/distributed-fs/openafs/src/config/param.rs_aix72.h

## Purpose
This AIX parameter header targets AIX 7.2. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
Later AIX 7.2/7.3 files include a clang-specific `free_sock_hash_table` macro workaround for broken AIX socket headers, so compiler matrix coverage matters.
The file is 181 lines and defines 90 preprocessor symbols. Its `SYS_NAME` is `"rs_aix72"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix72`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_AIX_ENV` = `1`
- `AFS_AIX32_ENV` = `1`
- `AFS_AIX41_ENV` = `1`
- `AFS_AIX42_ENV` = `1`
- `AFS_AIX51_ENV` = `1`
- `AFS_AIX52_ENV` = `1`
- `AFS_AIX53_ENV` = `1`
- `AFS_AIX61_ENV` = `1`
- `AFS_AIX71_ENV` = `1`
- `AFS_AIX72_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix72"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix72`
- `AFSBIG_ENDIAN` = `1`
- `RIOS` = `1	/* POWERseries 6000. (sj/pc)    */`
- `AFS_VM_RDWR_ENV` = `1	/* read/write implemented via VM */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `AFS_UIOFMODE` = `1`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_MINCHANGE` = `2`
- `AFS_KALLOC` = `kmem_alloc`
- `AFS_KFREE` = `kmem_free`
- `AFS_DIRENT` = ``
- `AFS_VFS_ENV` = `1`
- `RXK_LISTENER_ENV` = `1`

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `__clang__` enables compiler-specific AIX header workaround

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`.
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
