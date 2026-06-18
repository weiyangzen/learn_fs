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
