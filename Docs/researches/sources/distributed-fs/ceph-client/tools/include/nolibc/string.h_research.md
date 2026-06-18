# sources/distributed-fs/ceph-client/tools/include/nolibc/string.h

## Purpose
Provides core memory and string routines for nolibc, with weak implementations that architecture backends may override.

## APIs, Types, and Functions
Defines `memcmp`, weak `memmove`, weak `memcpy`, weak `memset`, `memchr`, `strchr`, `strcmp`, `strcpy`, weak `strlen`, `strnlen`, `strdup`, `strndup`, `strlcat`, `strlcpy`, `strncat`, `strncmp`, `strncpy`, `strrchr`, `strstr`, `tolower`, and `toupper`. It also has a `strlen` macro optimization for constant strings.

## Control Flow, State, and Persistence
Memory functions perform byte-wise forward/backward copies or fills. String functions scan until NUL or a requested limit, duplicate via `malloc`, and return libc-like pointers or lengths. Persistent state is only caller-owned buffers and heap allocations returned by duplication functions.

## Dependencies and Integration
Depends on `std.h`, `stddef.h`, and `stdlib` allocation for duplication. Architecture headers can mark `NOLIBC_ARCH_HAS_MEMMOVE`, `MEMCPY`, or `MEMSET` to replace weak generic versions.

## Risks and Test Signals
Risks include performance on large buffers, overlap misuse with `memcpy`, unsigned/signed char comparison differences, non-thread-safe assumptions around caller buffers, and incomplete locale handling for case conversion. Test signals are exhaustive small-buffer memory tests, overlap `memmove` cases, string boundary tests without NUL inside limits, strdup allocation failure paths, and architecture override builds.
