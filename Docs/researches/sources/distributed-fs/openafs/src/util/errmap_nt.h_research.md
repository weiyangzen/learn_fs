# sources/distributed-fs/openafs/src/util/errmap_nt.h

Purpose: Declares NT error translation and fills in POSIX `errno` constants missing from some Microsoft C runtime versions, using Winsock values or OpenAFS private values.

Important APIs and macros: Declares `nterr_nt2unix(long ntErr, int defaultErr)`. Defines socket-related errno aliases such as `EWOULDBLOCK`, `EINPROGRESS`, `ENOTSOCK`, `ECONNRESET`, `EHOSTUNREACH`, and private additions based at `AFS_NT_ERRNO_BASE` for `EOVERFLOW`, `ENOMSG`, `ETIME`, and `ENOTBLK`.

Control flow and state: Header-only compatibility layer. It is conditionally additive: values are defined only when the platform headers do not define them.

Dependencies and integration: Includes `<errno.h>` and expects Winsock constants like `WSAEWOULDBLOCK` and `WSABASEERR` to be visible through Windows networking headers in the including translation unit. Windows portability files include it before converting `GetLastError()` or socket errors.

Risks and test signals: The private errno namespace assumes no collision above `WSABASEERR + 1100`. Because the header references Winsock names, include ordering matters on Windows. No direct tests are present; compile coverage across Visual Studio variants is the main signal.
