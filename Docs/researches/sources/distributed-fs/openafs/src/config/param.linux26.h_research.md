# sources/distributed-fs/openafs/src/config/param.linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
The common file has a major `UKERNEL` split: libafs/kernel builds include `<linux/version.h>` and conditionally set `AFS_ATSYS_VFS_ENV` for Linux >= 3.10, while UKERNEL builds provide uio-field aliases, `VATTR_NULL`, `AFS_DIRENT`, and userspace defaults. It also probes errqueue/PMTU support and enables `USE_UCONTEXT` for glibc newer than 2.3.
The file is 111 lines and defines 48 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = ``
- `AFS_LINUX_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_NAMEI_ENV` = `1 /* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1 /* Set to Userdisabled, allow sysctl to override */`
- `AFS_PAG_ONEGROUP_ENV` = `1`
- `AFS_HAVE_FFS` = `1 /* Use system's ffs */`
- `AFS_HAVE_STATVFS` = `0 /* System doesn't support statvfs */`
- `AFS_VM_RDWR_ENV` = `1 /* read/write implemented via VM */`
- `AFS_USE_GETTIMEOFDAY` = `1 /* use gettimeofday to implement rx clock */`
- `AFS_MAXVCOUNT_ENV` = `1`
- `AFS_NEW_BKG` = `1`
- `AFS_PRIVATE_OSI_ALLOCSPACES` = `1`
- `AFS_GLOBAL_SUNLOCK` = ``
- `AFS_ATSYS_VFS_ENV` = ``
- `AFS_USR_LINUX_ENV` = `1`
- `AFS_ENV` = `1`
- `AFS_UIOSYS` = `1`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `MCLBYTES`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``
- `AFS_RXERRQ_ENV` = ``
- `AFS_ADAPT_PMTU` = ``
- `USE_UCONTEXT` = ``

It explicitly undefines: `AFS_NONFSTRANS`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<linux/version.h>`, `<features.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.
- For Linux common builds, verify errqueue/PMTU feature probes with configure results and runtime networking tests.
