# sources/distributed-fs/openafs/src/config/param.i386_umlinux26.h

## Purpose
This i386 UML architecture parameter header contributes the minimal Linux User Mode Linux identity: kernel builds receive `AFS_I386_LINUX_ENV`, UKERNEL builds define `UKERNEL`, and all builds get `SYS_NAME`, `SYS_NAME_ID`, Linux syscall slot 137, and little-endian identity.
It intentionally omits the broad Linux common feature surface found in `param.linux26.h`; it is an architecture selector that must be paired with Linux common configuration elsewhere.
The file is 31 lines and defines 7 preprocessor symbols. Its `SYS_NAME` is `"i386_umlinux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_umlinux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_I386_LINUX_ENV` = `1`
- `SYS_NAME` = `"i386_umlinux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_umlinux26`
- `AFS_SYSCALL` = `137`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
This file has no direct `#include`; it depends on being included alongside the appropriate OpenAFS common/platform headers and generated system-name table.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
