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
