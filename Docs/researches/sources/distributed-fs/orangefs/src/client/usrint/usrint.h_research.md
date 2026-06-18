## sources/distributed-fs/orangefs/src/client/usrint/usrint.h

Purpose: Central usrint umbrella header that normalizes feature macros, suppresses libc redirects for usrint implementation files, imports POSIX/PVFS dependencies, declares compatibility functions, and sets usrint configuration constants.

Important APIs, types, and functions: Defines `_GNU_SOURCE`, large-file and thread macros, `USRINT_SOURCE` behavior for `_FILE_OFFSET_BITS`, fortify, inline redirects, and glibc feature toggles. Declares `posix_readdir`, `fseek64`, `ftell64`, `pvfs_convert_iovec`, and possibly `dup3`. Defines PVFS/Linux filesystem magic constants, O flag fallbacks, `AT_*` fallbacks, booleans, `O_HINTS`, `O_NOTPVFS`, stdio/cache sizes, descriptor-table constants, and defaults for `PVFS_USRINT_BUILD`, `PVFS_USRINT_CWD`, `PVFS_USRINT_KMOUNT`, `PVFS_UCACHE_ENABLE`, and `PVFS_STDIO_REDEFSTREAM`.

Control flow: No runtime logic. Compile-time branches differ for usrint implementation (`USRINT_SOURCE`) versus consumers: implementation files disable libc's 64-bit redirection/inlining so they can define both native and 64-bit symbols; consumers default to 64-bit file offsets.

State and persistence: No runtime state, but macro choices determine ABI, symbol interposition, file-offset width, and cache/table sizes across the library.

Dependencies and integration points: Pulls in many libc/POSIX headers, optional ACL/xattr/SELinux headers, and OrangeFS headers (`pvfs2.h`, hints, debug, types, protocol, locks, env vars). Nearly all usrint C files include it.

Risks and test signals: Aggressively redefining feature and optimization macros is fragile with newer libc headers. Fallback xattr prototypes may conflict with platform declarations. `AT_REMOVDIR` fallback appears misspelled in the `#ifndef AT_REMOVDIR` branch. Test compilation across glibc versions, with/without SELinux/ACL/xattr headers, consumer vs implementation includes, large-file calls, and macro collision warnings.
