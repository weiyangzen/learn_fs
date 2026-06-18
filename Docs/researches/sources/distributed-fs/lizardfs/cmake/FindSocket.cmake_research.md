# sources/distributed-fs/lizardfs/cmake/FindSocket.cmake

## Purpose
This module locates Berkeley socket support, either as a libc function or via a separate socket library.

## Important APIs, Types, and Functions
It checks `socket()` with `check_function_exists`. If missing, it searches for `ws2_32` or `socket` in default paths and `${SOCKET_PREFIX}`. It sets `SOCKET_FOUND`, `SOCKET_LIBRARIES`, and `LIZARDFS_HAVE_SOCKET`.

## Control Flow and State
The module exits early if `SOCKET_FOUND` or `NO_SOCKET` is set. If `socket()` is in libc, it marks found with an empty library list. If not, it tries library discovery and either succeeds, fatals when required, or logs a skip message.

## Dependencies and Integration Points
`Libraries.cmake` requires `find_package(Socket REQUIRED)`. Socket variables feed link libraries for networking code and feature macros in `config.h.in`.

## Risks and Edge Cases
The line `set(LIZARDFS_HAVE_SOCKET)` in the library-found branch clears rather than sets the variable, which may be intentional or a bug depending on macro expectations. The search paths are minimal. The module spelling says "berkley" in comments but behavior is standard socket discovery.

## Test Signals
Required package failure stops configuration. Successful network target link on MinGW, illumos, or libc-socket systems validates behavior.
