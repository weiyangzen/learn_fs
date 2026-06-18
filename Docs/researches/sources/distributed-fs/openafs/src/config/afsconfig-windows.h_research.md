# sources/distributed-fs/openafs/src/config/afsconfig-windows.h

Purpose: hand-maintained Windows replacement for the Autoconf-generated `afsconfig.h`.

Important APIs/types/functions: defines Windows feature availability and portability shims such as `SIZEOF_LONG 4`, `inline __inline`, `HAVE_ERROR_MESSAGE`, Winsock and Windows headers, POSIX mode constants, `socklen_t`, older MSVC `errno_t`, roken/directory/string/time feature macros, `AFS_NAMEI_ENV`, `RENAME_DOES_NOT_UNLINK`, Heimdal credential fields, and `ROKEN_LIB_DYNAMIC`.

Control flow: no executable flow; it drives conditional compilation in Windows builds.

State and persistence: no runtime state. It fixes the compile-time feature matrix for Windows/Win2000-style builds.

Dependencies and integration: included as the Windows `afsconfig.h` equivalent across OpenAFS NT code and shared libraries. It integrates with roken, Heimdal, Winsock, and OpenAFS namei cache code.

Risks and test signals: risks include stale feature declarations as Windows SDK/MSVC behavior changes, duplicate `#undef` sections, and type conflicts for `socklen_t` or `errno_t`. Signals are full Windows builds across supported compiler versions and runtime smoke tests for networking, directory, rename, lstat, and Heimdal integration.
