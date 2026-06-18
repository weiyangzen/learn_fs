# sources/distributed-fs/openafs/src/config/param.i386_obsd37.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.7. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
Notable source-specific risk: this file defines `AFS_X8_ENV` instead of the otherwise consistent `AFS_X86_ENV`, so consumers expecting the normal x86 macro will not see it for this target.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd37"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd37`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd37"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd37`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X8_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

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
- Possible typo `AFS_X8_ENV` instead of `AFS_X86_ENV` may disable x86-specific conditional code.
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
