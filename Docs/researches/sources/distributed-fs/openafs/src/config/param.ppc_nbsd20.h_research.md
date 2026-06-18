# sources/distributed-fs/openafs/src/config/param.ppc_nbsd20.h

## Purpose
This NetBSD parameter header targets NetBSD 2.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 10 lines and defines 5 preprocessor symbols. Its `SYS_NAME` is `"macppc_nbsd20"` and its `SYS_NAME_ID` is `SYS_NAME_ID_macppc_nbsd20`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PPC_PARAM_H` = ``
- `SYS_NAME` = `"macppc_nbsd20"`
- `SYS_NAME_ID` = `SYS_NAME_ID_macppc_nbsd20`
- `AFS_PPC_ENV` = `1`
- `AFSBIG_ENDIAN` = `1`

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- Only include guards and unconditional platform definitions are present.

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
This file has no direct `#include`; it depends on being included alongside the appropriate OpenAFS common/platform headers and generated system-name table.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
