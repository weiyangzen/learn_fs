# sources/distributed-fs/openafs/src/config/param.sparc64_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 45 lines and defines 13 preprocessor symbols. Its `SYS_NAME` is `"sparc64_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sparc64_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_SPARC64_LINUX_ENV` = `1`
- `AFS_LINUX_64BIT_KERNEL` = `1`
- `AFS_64BITPOINTER_ENV` = `1	/* pointers are 64 bits. */`
- `AFS_32BIT_USR_ENV` = `1	/* user level processes are 32bit */`
- `SYS_NAME` = `"sparc64_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sparc64_linux26`
- `AFS_SYSCALL` = `227`
- `AFSBIG_ENDIAN` = `1`

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
This file has no direct `#include`; it depends on being included alongside the appropriate OpenAFS common/platform headers and generated system-name table.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Pointer-width macros must match the compiler ABI or ioctl/kernel-user structures can be mis-sized.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
