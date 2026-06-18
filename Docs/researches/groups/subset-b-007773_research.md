# subset-b-007773 OpenAFS config parameter header research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd32.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd32.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.2. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd32"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd32`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd32"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd32`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd33.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd33.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.3. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd33"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd33`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd33"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd33`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd33.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd34.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd34.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.4. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd34"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd34`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd34"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd34`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd34.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd35.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd35.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.5. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd35"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd35`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd35"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd35`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd36.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd36.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.6. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd36"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd36`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd36"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd36`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd37.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd37.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd38.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd38.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.8. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd38"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd38`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd38"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd38`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd38.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd39.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd39.h

## Purpose
This is the i386 architecture overlay for OpenBSD 3.9. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd39"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd39`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd39"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd39`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd39.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd40.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd40.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.0. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd40"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd40`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd40"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd40`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd41.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd41.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.1. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd41"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd41`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd41"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd41`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd41.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd42.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd42.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.2. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd42"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd42`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd42"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd42`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd43.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd43.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.3. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd43"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd43`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd43"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd43`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd44.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd44.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.4. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd44"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd44`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd44"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd44`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd44.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd45.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd45.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.5. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 16 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd45"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd45`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd45"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd45`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
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
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd45.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd46.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd46.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.6. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd46"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd46`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd46"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd46`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd46.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd47.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd47.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.7. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd47"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd47`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd47"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd47`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd47.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd48.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd48.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.8. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd48"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd48`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd48"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd48`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd48.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd49.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd49.h

## Purpose
This is the i386 architecture overlay for OpenBSD 4.9. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd49"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd49`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd49"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd49`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd49.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd50.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd50.h

## Purpose
This is the i386 architecture overlay for OpenBSD 5.0. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd50"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd50`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd50"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd50`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd51.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd51.h

## Purpose
This is the i386 architecture overlay for OpenBSD 5.1. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd51"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd51`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd51"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd51`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd51.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd52.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd52.h

## Purpose
This is the i386 architecture overlay for OpenBSD 5.2. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd52"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd52`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd52"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd52`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd52.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd53.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd53.h

## Purpose
This is the i386 architecture overlay for OpenBSD 5.3. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd53"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd53`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd53"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd53`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd53.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd54.h -->
# sources/distributed-fs/openafs/src/config/param.i386_obsd54.h

## Purpose
This is the i386 architecture overlay for OpenBSD 5.4. It supplies the machine-specific `SYS_NAME`, `SYS_NAME_ID`, x86-on-XBSD marker, and little-endian declaration that pair with the matching `param.obsd*.h` OpenBSD common header.
For `_KERNEL` builds it declares `bcopy` and provides a `static inline memmove` wrapper implemented via `bcopy`, compensating for OpenBSD kernel header/library availability in these later i386 targets.
There is no user/kernel split beyond the optional `_KERNEL` memory shim; downstream build logic gets all behavior from these constants.
The file is 25 lines and defines 6 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd54"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd54`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_I386_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd54"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd54`
- `AFS_X86_XBSD_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`

Additional API/type notes:
- `inline functions: static inline void *memmove(void *dst, const void *src, size_t len) {`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

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
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_obsd54.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_umlinux26.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_umlinux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_w2k.h -->
# sources/distributed-fs/openafs/src/config/param.i386_w2k.h

## Purpose
This Windows `param.i386_w2k.h` header maps the OpenAFS portability layer onto the Win32/MSVC runtime. It declares NT-family, little-endian, NAMEI, 64-bit inode operation, missing-statvfs, and Kerberos/error or integer-conversion capability macros, then includes `afs_sysnames.h` for the configured system-id token.
The exported API surface includes compatibility typedefs and libc shims: `ssize_t`, `caddr_t`, `MAXPATHLEN`, `lstat` mapped to `_stat` variants depending on `_MSC_VER` and `_USE_32BIT_TIME_T`, case-insensitive string aliases, sleep, random seeding, popen/pclose, and on the 64-bit header also `fsync`, `ftruncate`, `pipe`, and `snprintf` wrappers.
There is no kernel branch content for `UKERNEL`; all meaningful definitions live in the non-UKERNEL block for Windows userspace/server builds.
The file is 73 lines and defines 21 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_w2k`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_NT40_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_HAVE_STATVFS` = `0	/* System doesn't support statvfs */`
- `AFS_KRB5_ERROR_ENV` = `1   /* fetch_krb5_error_message() available in afsutil.lib */`
- `HAVE_SSIZE_T` = `1`
- `HAVE_INT64TOINT32` = `1`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_w2k`
- `MAXPATHLEN` = `_MAX_PATH`

Additional API/type notes:
- `typedefs: typedef int ssize_t;; typedef char *caddr_t;`
- POSIX compatibility macros for `lstat`, case-insensitive string compare, sleep, random, popen/pclose, and selected file APIs

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<stdlib.h>`, `<string.h>`, `<stddef.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Windows CRT mapping depends on compiler version and 32-bit versus 64-bit time settings.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i386_w2k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i64_w2k.h -->
# sources/distributed-fs/openafs/src/config/param.i64_w2k.h

## Purpose
This Windows `param.i64_w2k.h` header maps the OpenAFS portability layer onto the Win32/MSVC runtime. It declares NT-family, little-endian, NAMEI, 64-bit inode operation, missing-statvfs, and Kerberos/error or integer-conversion capability macros, then includes `afs_sysnames.h` for the configured system-id token.
The exported API surface includes compatibility typedefs and libc shims: `ssize_t`, `caddr_t`, `MAXPATHLEN`, `lstat` mapped to `_stat` variants depending on `_MSC_VER` and `_USE_32BIT_TIME_T`, case-insensitive string aliases, sleep, random seeding, popen/pclose, and on the 64-bit header also `fsync`, `ftruncate`, `pipe`, and `snprintf` wrappers.
There is no kernel branch content for `UKERNEL`; all meaningful definitions live in the non-UKERNEL block for Windows userspace/server builds.
The file is 76 lines and defines 23 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `SYS_NAME_ID_i64_w2k`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_NT40_ENV` = `1`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_HAVE_STATVFS` = `0	/* System doesn't support statvfs */`
- `HAVE_INT64TOINT32` = `1`
- `SYS_NAME_ID` = `SYS_NAME_ID_i64_w2k`
- `MAXPATHLEN` = `_MAX_PATH`

Additional API/type notes:
- `typedefs: typedef __int64 ssize_t;; typedef char *caddr_t;`
- POSIX compatibility macros for `lstat`, case-insensitive string compare, sleep, random, popen/pclose, and selected file APIs

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<stdlib.h>`, `<string.h>`, `<stddef.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Endian macro must match the actual architecture to avoid wire/cache data interpretation errors.
- Windows CRT mapping depends on compiler version and 32-bit versus 64-bit time settings.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.i64_w2k.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_hpux1122.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_hpux1122.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_hpux1123.h -->
# sources/distributed-fs/openafs/src/config/param.ia64_hpux1123.h

## Purpose
This IA-64 HP-UX header targets HP-UX 1123. It accumulates HP-UX release macros through 11.22/11.23, enables 64-bit client behavior and LP64 pointer markers when `__LP64__` is present, declares syscall slot 48, big-endian identity, statvfs/ffs support, rx listener, userspace IP address handling, global AFS locking, and gettimeofday-based rx clock behavior.
The `KERNEL` branch maps OpenAFS uio, allocation, and vnode-attribute abstraction names onto HP-UX kernel names, sets `_KERNEL`, declares `AFS_HPUX_64BIT_ENV` for LP64, and for non-UKERNEL kernel builds maps memset/memcpy/memcmp to bzero/bcopy/bcmp.
The header defines `EDQUOT` if missing and forces `USE_UCONTEXT`, so build tests must cover both HP-UX system headers and user context availability.
The file is 103 lines and defines 48 preprocessor symbols. Its `SYS_NAME` is `"ia64_hpux1123"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ia64_hpux1123`.

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
- `AFS_HPUX1123_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BITPOINTER_ENV` = `1	/* pointers are 64 bits. */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_SYSCALL` = `48 /* slot reserved for AFS */`
- `SYS_NAME` = `"ia64_hpux1123"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ia64_hpux1123`
- `AFSBIG_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_GCPAGS` = `0       /* if nonzero, garbage collect PAGs */`
- `AFS_USE_VOID_PTR` = `1`
- `AFS_TEXT_ENV` = `1	/* Older kernels use TEXT */`
- `AFS_USE_GETTIMEOFDAY` = `1  /* use gettimeofday to implement rx clock */`
- `NEARINODE_HINT` = `1   /* hint to ufs module to scatter inodes on disk*/`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_hpux1123.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.ia64_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 39 lines and defines 12 preprocessor symbols. Its `SYS_NAME` is `"ia64_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ia64_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_IA64_LINUX_ENV` = `1`
- `AFS_LINUX_64BIT_KERNEL` = `1`
- `AFS_64BITPOINTER_ENV` = `1	/* pointers are 64 bits. */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_MAXVCOUNT_ENV` = `1`
- `USE_UCONTEXT` = ``
- `SYS_NAME` = `"ia64_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ia64_linux26`
- `AFS_SYSCALL` = `1141`
- `AFSLITTLE_ENDIAN` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ia64_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.linux26.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd15.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd15.h

## Purpose
This NetBSD parameter header targets NetBSD 1.5. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 101 lines and defines 50 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = ``
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_KERBEROS_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_ENV` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `0	/* System doesn't supports statvfs */`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd15.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd16.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd16.h

## Purpose
This NetBSD parameter header targets NetBSD 1.6. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 102 lines and defines 51 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = ``
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_KERBEROS_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_ENV` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `0	/* System doesn't supports statvfs */`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd20.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd20.h

## Purpose
This NetBSD parameter header targets NetBSD 2.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 144 lines and defines 69 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_KERBEROS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``
- `AFS_USERSPACE_IP_ADDR` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd21.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd21.h

## Purpose
This NetBSD parameter header targets NetBSD 2.1. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 144 lines and defines 69 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_KERBEROS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``
- `AFS_USERSPACE_IP_ADDR` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd21.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd30.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd30.h

## Purpose
This NetBSD parameter header targets NetBSD 3.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 140 lines and defines 68 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``
- `AFS_USERSPACE_IP_ADDR` = `1`
- `RXK_LISTENER_ENV` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd30.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd40.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd40.h

## Purpose
This NetBSD parameter header targets NetBSD 4.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
The file is 146 lines and defines 70 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `318 /* 210 */`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NBSD40_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `RXK_LISTENER_ENV` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`
- `inline functions: #define inline`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd50.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd50.h

## Purpose
This NetBSD parameter header targets NetBSD 5.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
Source-specific risk: the userland include guard contains `!defined()` with an empty macro name, which is syntactically suspicious and should be compile-tested on the intended preprocessor.
The file is 142 lines and defines 71 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NBSD40_ENV` = `1`
- `AFS_NBSD50_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `RXK_LISTENER_ENV` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Suspicious empty `!defined()` preprocessor condition needs compiler validation.
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd60.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd60.h

## Purpose
This NetBSD parameter header targets NetBSD 6.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
Source-specific risk: the userland include guard contains `!defined()` with an empty macro name, which is syntactically suspicious and should be compile-tested on the intended preprocessor.
The file is 143 lines and defines 72 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NBSD40_ENV` = `1`
- `AFS_NBSD50_ENV` = `1`
- `AFS_NBSD60_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `RXK_LISTENER_ENV` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Suspicious empty `!defined()` preprocessor condition needs compiler validation.
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd60.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd70.h -->
# sources/distributed-fs/openafs/src/config/param.nbsd70.h

## Purpose
This NetBSD parameter header targets NetBSD 7.0. It accumulates NetBSD release macros, declares XBSD/NetBSD, NAMEI, 64-bit client and inode operations, syscall slot 210, non-fileserver translator mode, VFS support, ffs/statvfs capability, rx listener, gettimeofday clocking, and root inode mapping to `UFS_ROOTINO`.
The non-UKERNEL path covers kernel/libafs constants and legacy `_KERNEL_DEPRECATED` vnode/uio compatibility mappings; the UKERNEL path defines userspace IP/rx behavior, uio aliases, `VATTR_NULL`, `AFS_DIRENT`, `CMSERVERPREF`, and userland socket/mount/uio includes.
Source-specific risk: the userland include guard contains `!defined()` with an empty macro name, which is syntactically suspicious and should be compile-tested on the intended preprocessor.
The file is 146 lines and defines 74 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_COMMON_H` = `1`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_SYSCALL` = `210`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`
- `AFS_XBSD_ENV` = `1		/* {Free,Open,Net}BSD */`
- `AFS_NBSD_ENV` = `1`
- `AFS_NBSD15_ENV` = `1`
- `AFS_NBSD16_ENV` = `1`
- `AFS_NBSD20_ENV` = `1`
- `AFS_NBSD30_ENV` = `1`
- `AFS_NBSD40_ENV` = `1`
- `AFS_NBSD50_ENV` = `1`
- `AFS_NBSD60_ENV` = `1`
- `AFS_NBSD70_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_HAVE_STATVFS` = `1	/* System supports statvfs */`
- `FTRUNC` = `O_TRUNC`
- `RXK_LISTENER_ENV` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_GREEDY43_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_MINCHANGE` = `2`
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<afs/afs_sysnames.h>`, `<limits.h>`, `<sys/param.h>`, `<sys/types.h>`, `<sys/mount.h>`, `<sys/fcntl.h>`, `<netinet/in.h>`, `<sys/uio.h>`, `<sys/socket.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Suspicious empty `!defined()` preprocessor condition needs compiler validation.
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.
- Kernel structure field aliases are tightly coupled to OS header versions.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.nbsd70.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd31.h -->
# sources/distributed-fs/openafs/src/config/param.obsd31.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.1. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 50 lines and defines 16 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd31.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd32.h -->
# sources/distributed-fs/openafs/src/config/param.obsd32.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.2. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 49 lines and defines 17 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd32.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd33.h -->
# sources/distributed-fs/openafs/src/config/param.obsd33.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.3. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 53 lines and defines 18 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd33.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd34.h -->
# sources/distributed-fs/openafs/src/config/param.obsd34.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.4. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 53 lines and defines 19 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd34.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd35.h -->
# sources/distributed-fs/openafs/src/config/param.obsd35.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.5. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 53 lines and defines 19 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd35.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd36.h -->
# sources/distributed-fs/openafs/src/config/param.obsd36.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.6. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 55 lines and defines 21 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd36.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd37.h -->
# sources/distributed-fs/openafs/src/config/param.obsd37.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.7. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 56 lines and defines 22 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd37.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd38.h -->
# sources/distributed-fs/openafs/src/config/param.obsd38.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.8. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 57 lines and defines 23 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd38.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd39.h -->
# sources/distributed-fs/openafs/src/config/param.obsd39.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 3.9. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
This common OpenBSD header also carries a `SYS_NAME`/`SYS_NAME_ID` identity, which is unusual because most OpenBSD common files leave architecture identity to the `param.i386_obsd*.h` overlay.
The file is 61 lines and defines 26 preprocessor symbols. Its `SYS_NAME` is `"i386_obsd39"` and its `SYS_NAME_ID` is `SYS_NAME_ID_i386_obsd39`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `SYS_NAME` = `"i386_obsd39"`
- `SYS_NAME_ID` = `SYS_NAME_ID_i386_obsd39`
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd39.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd40.h -->
# sources/distributed-fs/openafs/src/config/param.obsd40.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.0. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 57 lines and defines 25 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd40.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd41.h -->
# sources/distributed-fs/openafs/src/config/param.obsd41.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.1. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 60 lines and defines 26 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd41.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd42.h -->
# sources/distributed-fs/openafs/src/config/param.obsd42.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.2. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 65 lines and defines 27 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd43.h -->
# sources/distributed-fs/openafs/src/config/param.obsd43.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.3. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 66 lines and defines 28 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd43.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd44.h -->
# sources/distributed-fs/openafs/src/config/param.obsd44.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.4. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 67 lines and defines 29 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd44.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd45.h -->
# sources/distributed-fs/openafs/src/config/param.obsd45.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.5. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 67 lines and defines 30 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd45.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd46.h -->
# sources/distributed-fs/openafs/src/config/param.obsd46.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.6. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 72 lines and defines 31 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`, `<sys/proc.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd46.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd47.h -->
# sources/distributed-fs/openafs/src/config/param.obsd47.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.7. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 73 lines and defines 32 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`, `<sys/proc.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd47.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd48.h -->
# sources/distributed-fs/openafs/src/config/param.obsd48.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.8. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 70 lines and defines 33 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd48.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd49.h -->
# sources/distributed-fs/openafs/src/config/param.obsd49.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 4.9. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 71 lines and defines 34 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd49.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd50.h -->
# sources/distributed-fs/openafs/src/config/param.obsd50.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 5.0. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 72 lines and defines 35 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_OBSD50_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd50.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd51.h -->
# sources/distributed-fs/openafs/src/config/param.obsd51.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 5.1. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 73 lines and defines 36 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_OBSD50_ENV` = `1`
- `AFS_OBSD51_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`
- `AFS_GLOBAL_SUNLOCK` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd51.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd52.h -->
# sources/distributed-fs/openafs/src/config/param.obsd52.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 5.2. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 74 lines and defines 37 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_OBSD50_ENV` = `1`
- `AFS_OBSD51_ENV` = `1`
- `AFS_OBSD52_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`
- `AFS_USE_GETTIMEOFDAY` = `1	/* use gettimeofday to implement rx clock */`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd52.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd53.h -->
# sources/distributed-fs/openafs/src/config/param.obsd53.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 5.3. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 75 lines and defines 38 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_OBSD50_ENV` = `1`
- `AFS_OBSD51_ENV` = `1`
- `AFS_OBSD52_ENV` = `1`
- `AFS_OBSD53_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `0	/* if nonzero, garbage collect PAGs */`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd53.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd54.h -->
# sources/distributed-fs/openafs/src/config/param.obsd54.h

## Purpose
This is the OpenBSD common platform parameter header for OpenBSD 5.4. It declares the XBSD/OpenBSD environment, NAMEI cache interface, 64-bit client and inode-operation support, OpenBSD release compatibility macros up to this file, VFS inclusion, syscall number 208, rx listener support, and gettimeofday-based rx clock behavior.
The `_KERNEL` branch only contributes compatibility definitions such as `AFS_GLOBAL_SUNLOCK` under `MULTIPROCESSOR` and `enum vcexcl` when not assembling; later releases add `sys/queue.h` for `TAILQ_ENTRY` and `sys/proc.h` when `curproc` is absent.
The file is 76 lines and defines 39 preprocessor symbols. Its `SYS_NAME` is `(none)` and its `SYS_NAME_ID` is `(none)`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_XBSD_ENV` = `1	/* {Free,Open,Net}BSD */`
- `AFS_NAMEI_ENV` = `1	/* User space interface to file system */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* Needed for NAMEI */`
- `AFS_OBSD_ENV` = `1`
- `AFS_OBSD31_ENV` = `1`
- `AFS_OBSD32_ENV` = `1`
- `AFS_OBSD33_ENV` = `1`
- `AFS_OBSD34_ENV` = `1`
- `AFS_OBSD35_ENV` = `1`
- `AFS_OBSD36_ENV` = `1`
- `AFS_OBSD37_ENV` = `1`
- `AFS_OBSD38_ENV` = `1`
- `AFS_OBSD39_ENV` = `1`
- `AFS_OBSD40_ENV` = `1`
- `AFS_OBSD41_ENV` = `1`
- `AFS_OBSD42_ENV` = `1`
- `AFS_OBSD43_ENV` = `1`
- `AFS_OBSD44_ENV` = `1`
- `AFS_OBSD45_ENV` = `1`
- `AFS_OBSD46_ENV` = `1`
- `AFS_OBSD47_ENV` = `1`
- `AFS_OBSD48_ENV` = `1`
- `AFS_OBSD49_ENV` = `1`
- `AFS_OBSD50_ENV` = `1`
- `AFS_OBSD51_ENV` = `1`
- `AFS_OBSD52_ENV` = `1`
- `AFS_OBSD53_ENV` = `1`
- `AFS_OBSD54_ENV` = `1`
- `AFS_NONFSTRANS` = `1`
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `FTRUNC` = `O_TRUNC`
- `AFS_SYSCALL` = `208`
- `RXK_LISTENER_ENV` = `1`

It explicitly undefines: `AFS_NONFSTRANS`.

Additional API/type notes:
- `enums: enum vcexcl { NONEXCL, EXCL };`

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `_KERNEL` adds native kernel compatibility definitions
- `MULTIPROCESSOR` enables OpenBSD global locking where present

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<sys/param.h>`, `<afs/afs_sysnames.h>`, `<sys/queue.h>`.
It integrates with OpenAFS build selection, `afs/afs_sysnames.h`, libafs kernel code, rx networking code, vnode/uio portability wrappers, NAMEI cache code, and userland/UKERNEL builds that need the same platform identity.

## Risks
- Hard-coded `AFS_SYSCALL` value must match the target kernel/user ABI.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.obsd54.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc64_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.ppc64_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 33 lines and defines 10 preprocessor symbols. Its `SYS_NAME` is `"ppc64_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ppc64_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_PPC64_LINUX_ENV` = `1`
- `AFS_LINUX_64BIT_KERNEL` = `1`
- `AFS_64BITPOINTER_ENV` = `1     /* pointers are 64 bits */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `SYS_NAME` = `"ppc64_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc64_linux26`
- `AFSBIG_ENDIAN` = `1`
- `AFS_SYSCALL` = `137`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc64_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc64le_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.ppc64le_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 31 lines and defines 8 preprocessor symbols. Its `SYS_NAME` is `"ppc64le_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ppc64le_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_PPC64_LINUX_ENV` = `1`
- `AFS_LINUX_64BIT_KERNEL` = `1`
- `AFS_64BITPOINTER_ENV` = `1     /* pointers are 64 bits */`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `SYS_NAME` = `"ppc64le_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc64le_linux26`

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
- Pointer-width macros must match the compiler ABI or ioctl/kernel-user structures can be mis-sized.

## Test Signals
- Compile preprocessing test for this header under the intended OS, architecture, and kernel/userland macro set.
- Verify `SYS_NAME_ID` resolves from `afs/afs_sysnames.h` when the header includes or pairs with that table.
- Build both non-UKERNEL and UKERNEL variants so the split branches stay valid.
- Build a kernel/libafs object that touches uio, vnode, allocation, and locking aliases from this header.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc64le_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_70.h -->
# sources/distributed-fs/openafs/src/config/param.ppc_darwin_70.h

## Purpose
This Darwin/macOS parameter header targets Darwin 70 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 124 lines and defines 79 preprocessor symbols. Its `SYS_NAME` is `"ppc_darwin_70"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ppc_darwin_70`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `SYS_NAME` = `"ppc_darwin_70"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_70`
- `AFSBIG_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`
- `AFS_UIOSYS` = `UIO_SYSSPACE`
- `AFS_UIOUSER` = `UIO_USERSPACE`
- `AFS_CLBYTES` = `CLBYTES`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = ``
- `AFS_USERSPACE_ENV` = ``
- `AFS_USR_DARWIN_ENV` = ``
- `AFS_USR_DARWIN70_ENV` = ``
- `AFS_DIRENT` = ``
- `CMSERVERPREF` = ``

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_70.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_80.h -->
# sources/distributed-fs/openafs/src/config/param.ppc_darwin_80.h

## Purpose
This Darwin/macOS parameter header targets Darwin 80 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 168 lines and defines 105 preprocessor symbols. Its `SYS_NAME` is `"x86_darwin_80"` and its `SYS_NAME_ID` is `SYS_NAME_ID_x86_darwin_80`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `SYS_NAME` = `"ppc_darwin_80"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_80`
- `AFSBIG_ENDIAN` = `1`
- `sys_x86_darwin_12` = `1`
- `sys_x86_darwin_13` = `1`
- `sys_x86_darwin_14` = `1`
- `sys_x86_darwin_60` = `1`
- `sys_x86_darwin_70` = `1`
- `sys_x86_darwin_80` = `1`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`
- `AFS_GCPAGS` = `0`
- `RXK_LISTENER_ENV` = `1`
- `RXK_TIMEDSLEEP_ENV` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_VFS34` = `1	/* What is VFS34??? */`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_80.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_90.h -->
# sources/distributed-fs/openafs/src/config/param.ppc_darwin_90.h

## Purpose
This Darwin/macOS parameter header targets Darwin 90 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 173 lines and defines 111 preprocessor symbols. Its `SYS_NAME` is `"x86_darwin_90"` and its `SYS_NAME_ID` is `SYS_NAME_ID_x86_darwin_90`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `SYS_NAME` = `"ppc_darwin_90"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_90`
- `AFSBIG_ENDIAN` = `1`
- `sys_x86_darwin_12` = `1`
- `sys_x86_darwin_13` = `1`
- `sys_x86_darwin_14` = `1`
- `sys_x86_darwin_60` = `1`
- `sys_x86_darwin_70` = `1`
- `sys_x86_darwin_80` = `1`
- `sys_x86_darwin_90` = `1`
- `AFSLITTLE_ENDIAN` = `1`
- `AFS_HAVE_FFS` = `1	/* Use system's ffs. */`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_darwin_90.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.ppc_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 31 lines and defines 7 preprocessor symbols. Its `SYS_NAME` is `"ppc_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_ppc_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_PPC_LINUX_ENV` = `1`
- `SYS_NAME` = `"ppc_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_linux26`
- `AFS_SYSCALL` = `137`
- `AFSBIG_ENDIAN` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_nbsd16.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_nbsd16.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_nbsd20.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.ppc_nbsd20.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix42.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix42.h

## Purpose
This AIX parameter header targets AIX 4.2. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 161 lines and defines 79 preprocessor symbols. Its `SYS_NAME` is `"rs_aix42"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix42`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_AIX_ENV` = `1`
- `AFS_AIX32_ENV` = `1`
- `AFS_AIX41_ENV` = `1`
- `AFS_AIX42_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix42"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix42`
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
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_ENV` = `1`
- `AFS_USR_AIX_ENV` = `1`
- `AFS_USR_AIX41_ENV` = `1`
- `AFS_USR_AIX42_ENV` = `1`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `sys_rs_aix42` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix42.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix51.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix51.h

## Purpose
This AIX parameter header targets AIX 5.1. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 168 lines and defines 85 preprocessor symbols. Its `SYS_NAME` is `"rs_aix51"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix51`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_AIX_ENV` = `1`
- `AFS_AIX32_ENV` = `1`
- `AFS_AIX41_ENV` = `1`
- `AFS_AIX42_ENV` = `1`
- `AFS_AIX51_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix51"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix51`
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
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_ENV` = `1`
- `AFS_USR_AIX_ENV` = `1`
- `AFS_USR_AIX41_ENV` = `1`
- `AFS_USR_AIX42_ENV` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix51.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix52.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix52.h

## Purpose
This AIX parameter header targets AIX 5.2. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 169 lines and defines 86 preprocessor symbols. Its `SYS_NAME` is `"rs_aix51"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix51`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_AIX_ENV` = `1`
- `AFS_AIX32_ENV` = `1`
- `AFS_AIX41_ENV` = `1`
- `AFS_AIX42_ENV` = `1`
- `AFS_AIX51_ENV` = `1`
- `AFS_AIX52_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix52"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix52`
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
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_ENV` = `1`
- `AFS_USR_AIX_ENV` = `1`
- `AFS_USR_AIX41_ENV` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix52.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix53.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix53.h

## Purpose
This AIX parameter header targets AIX 5.3. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 170 lines and defines 87 preprocessor symbols. Its `SYS_NAME` is `"rs_aix51"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix51`.

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
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix53"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix53`
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
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_ENV` = `1`
- `AFS_USR_AIX_ENV` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix53.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix61.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix61.h

## Purpose
This AIX parameter header targets AIX 6.1. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 171 lines and defines 88 preprocessor symbols. Its `SYS_NAME` is `"rs_aix51"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix51`.

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
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix61"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix61`
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
- `AFS_USERSPACE_IP_ADDR` = `1`
- `AFS_ENV` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix61.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix71.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix71.h

## Purpose
This AIX parameter header targets AIX 7.1. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
The file is 172 lines and defines 89 preprocessor symbols. Its `SYS_NAME` is `"rs_aix71"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix71`.

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
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix71"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix71`
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
- `AFS_USERSPACE_IP_ADDR` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix71.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix72.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix72.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix73.h -->
# sources/distributed-fs/openafs/src/config/param.rs_aix73.h

## Purpose
This AIX parameter header targets AIX 7.3. It accumulates AIX release macros, declares AIX 32-bit environment, 64-bit client/NAMEI/64-bit inode operations, flock sysid support, global AFS lock, PAG garbage collection, filesystem number 4, syscall number 31 for kernel and 105 for the userspace branch, big-endian identity, VM read/write, statvfs, and gettimeofday clocking.
The non-UKERNEL branch maps uio fields, allocation, vnode attributes, and vnode node id fields for AIX kernel builds; the UKERNEL branch emits AIX userspace markers, userspace IP/rx settings, disk inode spare usage, and uio aliases when compiled with `KERNEL`.
Later AIX 7.2/7.3 files include a clang-specific `free_sock_hash_table` macro workaround for broken AIX socket headers, so compiler matrix coverage matters.
The file is 182 lines and defines 91 preprocessor symbols. Its `SYS_NAME` is `"rs_aix73"` and its `SYS_NAME_ID` is `SYS_NAME_ID_rs_aix73`.

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
- `AFS_AIX73_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_NAMEI_ENV` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_FSNO` = `4`
- `AFS_SYSCALL` = `31`
- `SYS_NAME` = `"rs_aix73"`
- `SYS_NAME_ID` = `SYS_NAME_ID_rs_aix73`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.rs_aix73.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.s390_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.s390_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 31 lines and defines 7 preprocessor symbols. Its `SYS_NAME` is `"s390_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_s390_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_S390_LINUX_ENV` = `1`
- `SYS_NAME` = `"s390_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_s390_linux26`
- `AFS_SYSCALL` = `137`
- `AFSBIG_ENDIAN` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.s390_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.s390x_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.s390x_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 40 lines and defines 14 preprocessor symbols. Its `SYS_NAME` is `"s390x_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_s390x_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_S390_LINUX_ENV` = `1`
- `AFS_S390X_LINUX_ENV` = `1`
- `AFS_64BITPOINTER_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_LINUX_64BIT_KERNEL` = `1`
- `SYS_NAME` = `"s390x_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_s390x_linux26`
- `AFS_SYSCALL` = `137`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.s390x_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sgi_65.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sgi_65.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sparc64_linux26.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sparc64_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sparc_linux26.h -->
# sources/distributed-fs/openafs/src/config/param.sparc_linux26.h

## Purpose
This Linux 2.6-style parameter header is either the common Linux platform header or an architecture overlay for Linux 2.6-style build target. It declares Linux environment markers, NAMEI/64-bit inode operation support, non-fileserver translator mode, userspace IP support, rx listener support, PAG behavior, ffs/statvfs capability, VM read/write, background daemon behavior, and the architecture-specific `SYS_NAME`/`SYS_NAME_ID` when present.
As an architecture overlay it mostly sets architecture, pointer-width, syscall, endian, and `SYS_NAME` macros; the broader Linux behavior is supplied by `param.linux26.h`. Several 64-bit overlays set `AFS_LINUX_64BIT_KERNEL`, pointer-width markers, or 32-bit user ABI flags.
The file is 42 lines and defines 10 preprocessor symbols. Its `SYS_NAME` is `"sparc_linux26"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sparc_linux26`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_SPARC_LINUX_ENV` = `1`
- `SYS_NAME` = `"sparc_linux26"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sparc_linux26`
- `AFS_SYSCALL` = `227`
- `AFSBIG_ENDIAN` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sparc_linux26.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_510.h -->
# sources/distributed-fs/openafs/src/config/param.sun4x_510.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 510 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 170 lines and defines 91 preprocessor symbols. Its `SYS_NAME` is `"sun4x_59"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sun4x_59`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_SUN510_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_CACHE_VNODE_PATH` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_SYSCALL` = `65`
- `sys_sun4x_510` = `1`
- `SYS_NAME` = `"sun4x_510"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sun4x_510`
- `AFSBIG_ENDIAN` = `1`
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
- `AFS_SUN5_64BIT_ENV` = `1`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_510.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_511.h -->
# sources/distributed-fs/openafs/src/config/param.sun4x_511.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 511 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 176 lines and defines 93 preprocessor symbols. Its `SYS_NAME` is `"sun4x_511"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sun4x_511`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_SUN510_ENV` = `1`
- `AFS_SUN511_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `BSD_COMP` = ``
- `AFS_CACHE_VNODE_PATH` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_PAG_ONEGROUP_ENV` = `1	/* Use a single gid to indicate a PAG */`
- `sys_sun4x_511` = `1`
- `SYS_NAME` = `"sun4x_511"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sun4x_511`
- `AFSBIG_ENDIAN` = `1`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_511.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_58.h -->
# sources/distributed-fs/openafs/src/config/param.sun4x_58.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 58 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 156 lines and defines 88 preprocessor symbols. Its `SYS_NAME` is `"sun4x_58"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sun4x_58`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_SYSCALL` = `65`
- `sys_sun4x_58` = `1`
- `SYS_NAME` = `"sun4x_58"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sun4x_58`
- `AFSBIG_ENDIAN` = `1`
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
- `AFS_SUN5_64BIT_ENV` = `1`
- `AFS_64BIT_INO` = `1`
- `AFS_KALLOC` = ``
- `AFS_KFREE` = `kmem_free`

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_58.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_59.h -->
# sources/distributed-fs/openafs/src/config/param.sun4x_59.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 59 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 158 lines and defines 90 preprocessor symbols. Its `SYS_NAME` is `"sun4x_59"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sun4x_59`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_SYSCALL` = `65`
- `sys_sun4x_59` = `1`
- `SYS_NAME` = `"sun4x_59"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sun4x_59`
- `AFSBIG_ENDIAN` = `1`
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
- `AFS_SUN5_64BIT_ENV` = `1`
- `AFS_64BIT_INO` = `1`
- `AFS_KALLOC` = ``

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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sun4x_59.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_510.h -->
# sources/distributed-fs/openafs/src/config/param.sunx86_510.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 510 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 168 lines and defines 90 preprocessor symbols. Its `SYS_NAME` is `"sunx86_510"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sunx86_510`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_SUN510_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_CACHE_VNODE_PATH` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_SYSCALL` = `65`
- `sys_sunx86_510` = `1`
- `SYS_NAME` = `"sunx86_510"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sunx86_510`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_510.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_511.h -->
# sources/distributed-fs/openafs/src/config/param.sunx86_511.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 511 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 173 lines and defines 92 preprocessor symbols. Its `SYS_NAME` is `"sunx86_511"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sunx86_511`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_SUN510_ENV` = `1`
- `AFS_SUN511_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_CACHE_VNODE_PATH` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_PAG_ONEGROUP_ENV` = `1	/* Use a single gid to indicate a PAG */`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `BSD_COMP` = ``
- `sys_sunx86_511` = `1`
- `SYS_NAME` = `"sunx86_511"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sunx86_511`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_511.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_58.h -->
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_58.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_59.h -->
# sources/distributed-fs/openafs/src/config/param.sunx86_59.h

## Purpose
This Solaris/SunOS parameter header targets Solaris/SunOS 59 on SPARC/sun4x or x86/sunx86. It declares VFS behavior, SunOS release macros, architecture identity, 64-bit client behavior, flock sysid support, NAMEI-related 64-bit inode operations, statvfs/statvfs64, vxfs cache support, VM read/write, gettimeofday clocking, global AFS locking, PAG handling, and system identity macros.
The non-UKERNEL branch maps Solaris uio fields, allocation with `kmem_alloc`, vnode attributes, root inode, and 64-bit inode behavior for 64-bit kernel compiles. The UKERNEL branch emits `AFS_USR_SUN*` release markers, userspace IP/rx settings, uio aliases, statvfs flags, `AFS_DIRENT`, `CMSERVERPREF`, and root inode mapping.
NAMEI builds define `nearInodeHash`, using volume id bits to scatter cache inodes, so cache distribution and inode-spare behavior are part of the persistence-sensitive surface.
The file is 169 lines and defines 89 preprocessor symbols. Its `SYS_NAME` is `"sunx86_59"` and its `SYS_NAME_ID` is `SYS_NAME_ID_sunx86_59`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_VFS_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1	/* NOBODY uses this.... */`
- `AFS_GREEDY43_ENV` = `1	/* Used only in rx/rx_user.c */`
- `AFS_ENV` = `1`
- `AFS_SUN_ENV` = `1`
- `AFS_SUN5_ENV` = `1`
- `AFS_SUN59_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_HAVE_FLOCK_SYSID` = `1`
- `AFS_GLOBAL_SUNLOCK` = `1	/* For global locking */`
- `RXK_LISTENER_ENV` = `1`
- `AFS_GCPAGS` = `1	/* if nonzero, garbage collect PAGs */`
- `AFS_64BIT_IOPS_ENV` = `1	/* needed for NAMEI... */`
- `AFS_3DISPARES` = `1	/* Utilize the 3 available disk inode 'spares' */`
- `AFS_SYSCALL` = `65`
- `sys_sunx86_59` = `1`
- `SYS_NAME` = `"sunx86_59"`
- `SYS_NAME_ID` = `SYS_NAME_ID_sunx86_59`
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

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.sunx86_59.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_100.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_100.h

## Purpose
This Darwin/macOS parameter header targets Darwin 100 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 228 lines and defines 159 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_100"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_100`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_VFSINCL_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`
- `AFSBIG_ENDIAN` = `1`
- `sys_ppc64_darwin_100` = `1`
- `sys_x86_darwin_12` = `1`
- `sys_x86_darwin_13` = `1`
- `sys_x86_darwin_14` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_100.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_110.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_110.h

## Purpose
This Darwin/macOS parameter header targets Darwin 110 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 233 lines and defines 164 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_110"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_110`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`
- `AFSBIG_ENDIAN` = `1`
- `sys_ppc64_darwin_100` = `1`
- `sys_x86_darwin_12` = `1`
- `sys_x86_darwin_13` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_110.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_120.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_120.h

## Purpose
This Darwin/macOS parameter header targets Darwin 120 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 239 lines and defines 170 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_120"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_120`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`
- `AFSBIG_ENDIAN` = `1`
- `sys_ppc64_darwin_100` = `1`
- `sys_x86_darwin_12` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_120.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_130.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_130.h

## Purpose
This Darwin/macOS parameter header targets Darwin 130 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 245 lines and defines 176 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_130"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_130`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`
- `AFSBIG_ENDIAN` = `1`
- `sys_ppc64_darwin_100` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_130.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_140.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_140.h

## Purpose
This Darwin/macOS parameter header targets Darwin 140 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 251 lines and defines 182 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_140"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_140`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_DARWIN140_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`
- `AFSBIG_ENDIAN` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_140.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_150.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_150.h

## Purpose
This Darwin/macOS parameter header targets Darwin 150 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 257 lines and defines 188 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_150"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_150`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_DARWIN140_ENV` = ``
- `AFS_DARWIN150_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`
- `SYS_NAME_ID` = `SYS_NAME_ID_ppc_darwin_100`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_150.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_160.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_160.h

## Purpose
This Darwin/macOS parameter header targets Darwin 160 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 263 lines and defines 194 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_160"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_160`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_DARWIN140_ENV` = ``
- `AFS_DARWIN150_ENV` = ``
- `AFS_DARWIN160_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`
- `SYS_NAME` = `"ppc_darwin_100"`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_160.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_170.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_170.h

## Purpose
This Darwin/macOS parameter header targets Darwin 170 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 269 lines and defines 200 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_170"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_170`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_DARWIN140_ENV` = ``
- `AFS_DARWIN150_ENV` = ``
- `AFS_DARWIN160_ENV` = ``
- `AFS_DARWIN170_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`
- `sys_ppc_darwin_100` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_170.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_180.h -->
# sources/distributed-fs/openafs/src/config/param.x86_darwin_180.h

## Purpose
This Darwin/macOS parameter header targets Darwin 180 while retaining compatibility macros for older Darwin releases. It selects PPC, x86, or amd64 at compile time, declares 64-bit client and inode operation behavior, NAMEI cache support, non-fileserver translator mode, syscall slot 230, Darwin refbase, warning behavior, vnode cache path support, new background daemon behavior, and endianness/system-id macros per architecture branch.
The file has a complete non-UKERNEL kernel/libafs branch and a UKERNEL userspace branch. Kernel builds include `<kern/macro_help.h>`, map uio/vnode/vfs fields to Darwin names, provide `_MALLOC`/`_FREE` allocation macros, and define `BIND_8_COMPAT`; UKERNEL builds use `AFS_USR_DARWIN*` release markers, userspace IP/rx constants, `AFS_DIRENT`, and root inode mapping.
Architecture branching is a major integration surface: the same header can emit PPC, PPC64, i386, or amd64 `SYS_NAME` values, so tests must compile all supported compiler predefined-macro paths for the target release.
The file is 275 lines and defines 206 preprocessor symbols. Its `SYS_NAME` is `"amd64_darwin_180"` and its `SYS_NAME_ID` is `SYS_NAME_ID_amd64_darwin_180`.

## Important APIs, Types, and Macros
This header is a compile-time contract, not a runtime module. Important exported definitions include:
- `AFS_PARAM_H` = ``
- `AFS_ENV` = `1`
- `AFS_64BIT_ENV` = `1	/* Defines afs_int32 as int, not long. */`
- `AFS_64BIT_CLIENT` = `1`
- `AFS_64BIT_IOPS_ENV` = `1`
- `AFS_PPC_ENV` = `1`
- `AFS_X86_ENV` = `1`
- `AFS_64BITUSERPOINTER_ENV` = `1`
- `AFS_64BIT_SIZEOF` = `1 /* seriously? */`
- `AFS_DARWIN_ENV` = ``
- `AFS_DARWIN70_ENV` = ``
- `AFS_DARWIN80_ENV` = ``
- `AFS_DARWIN90_ENV` = ``
- `AFS_DARWIN100_ENV` = ``
- `AFS_DARWIN110_ENV` = ``
- `AFS_DARWIN120_ENV` = ``
- `AFS_DARWIN130_ENV` = ``
- `AFS_DARWIN140_ENV` = ``
- `AFS_DARWIN150_ENV` = ``
- `AFS_DARWIN160_ENV` = ``
- `AFS_DARWIN170_ENV` = ``
- `AFS_DARWIN180_ENV` = ``
- `AFS_NONFSTRANS` = ``
- `AFS_SYSCALL` = `230`
- `AFS_NAMEI_ENV` = `1`
- `AFS_WARNUSER_MARINER_ENV` = `1`
- `AFS_CACHE_VNODE_PATH` = ``
- `AFS_NEW_BKG` = `1`
- `NEED_IOCTL32` = ``
- `sys_ppc_darwin_12` = `1`
- `sys_ppc_darwin_13` = `1`
- `sys_ppc_darwin_14` = `1`
- `sys_ppc_darwin_60` = `1`
- `sys_ppc_darwin_70` = `1`
- `sys_ppc_darwin_80` = `1`
- `sys_ppc_darwin_90` = `1`

It explicitly undefines: `AFS_NONFSTRANS`, `MACRO_BEGIN`, `MACRO_END`, `AFS_NONFSTRANS`.

Additional API/type notes:
- No C functions or structs are implemented; the public surface is preprocessor macros consumed by OpenAFS portability code.

## Control Flow
There is no runtime control flow. Compile-time control is handled by include guards and conditional preprocessing branches:
- `UKERNEL` separates kernel/libafs and userspace-kernel builds
- `KERNEL` adds kernel-specific uio/vnode/allocation mappings
- `__amd64__` selects amd64/x86_64 identity and user pointer width
- `__i386__` selects i386 identity
- `__ppc__` selects PowerPC identity

## State and Persistence Behavior
The file owns no mutable state and performs no I/O. Its state impact is indirect: macros such as `AFS_NAMEI_ENV`, `AFS_64BIT_IOPS_ENV`, `AFS_NONFSTRANS`, `AFS_GCPAGS`, `AFS_FSNO`, `ROOTINO`, syscall numbers, endian flags, and vnode/uio aliases determine how OpenAFS interprets cache files, inode identifiers, PAG handling, kernel calls, and kernel/user ABI structures on this platform.

## Dependencies and Integration Points
Direct includes: `<afs/afs_sysnames.h>`, `<kern/macro_help.h>`, `<afs/afs_sysnames.h>`.
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
- Run or compile NAMEI cache-path code because 64-bit inode operation and cache layout macros are enabled.
- Exercise PAG/token setup paths because this header chooses the default PAG garbage-collection behavior.

<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/config/param.x86_darwin_180.h -->
