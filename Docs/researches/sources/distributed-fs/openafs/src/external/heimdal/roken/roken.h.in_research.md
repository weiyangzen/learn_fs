# sources/distributed-fs/openafs/src/external/heimdal/roken/roken.h.in

## Purpose
Template for the generated public roken header. It collects platform headers, defines roken socket and allocator abstractions, maps missing libc/POSIX APIs to `rk_*` implementations, and declares the portability surface used by Heimdal-derived code inside OpenAFS.

## Important APIs, Types, And Functions
It defines `rk_socket_t`, `rk_closesocket`, socket error macros, `rk_SOCK_INIT`, `rk_SOCK_EXIT`, MSVC integer and POSIX-like types, `ssize_t`, `rk_UNCONST`, WinSock `msghdr`/`sendmsg_w32`, allocator wrappers, string wrappers, `strerror_r` compatibility, network address APIs, passwd/group helpers, pidfile, byte-swap, flock, `net_read`, `net_write`, getopt globals, `addrinfo` and `sockaddr_storage` fallbacks, time/date functions, `setprogname`/`getprogname`, vis/unvis APIs, `closefrom`, `timegm`, tree-search macros, random macros, and Linux `SOCK_CLOEXEC` socket wrapping.

## Control Flow
The file is preprocessor-driven. Configure macros decide whether names such as `setenv`, `snprintf`, `strlcpy`, `mkstemp`, `getaddrinfo`, or `tsearch` resolve to native functions or roken replacements.

## State And Persistence
The header creates no state directly. It exposes state-bearing APIs for environment variables, pid files, sockets, random number initialization, memory allocation, and program-name globals.

## Dependencies And Integration Points
Generated from the build system and included by nearly every roken source file. It is the ABI and macro contract between OpenAFS, vendored Heimdal code, system C libraries, WinSock, and MSVC runtime quirks.

## Risks And Test Signals
Because it remaps standard function names, include order and feature-test accuracy are critical. Risks include prototype drift, accidental macro substitution in third-party headers, allocator mismatch on Windows, and wrong socket-handle assumptions. Test signals include all supported platform builds, configure-header regeneration, compile checks with `ROKEN_NO_DEFINE_ALLOCATORS`, and runtime tests for the replacement APIs.
