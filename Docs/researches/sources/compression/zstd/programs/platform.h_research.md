# sources/compression/zstd/programs/platform.h

## Purpose

This portability header normalizes compiler, large-file, POSIX, console, binary-mode, sparse-file, symbol-list, priority, and sleep feature detection for zstd programs.

## Important APIs, Types, and Functions

It defines MSVC warning/security compatibility macros, detects 64-bit targets, enables large-file macros on 32-bit systems, computes `PLATFORM_POSIX_VERSION`, exposes `IS_CONSOLE()`, `SET_BINARY_MODE()`, `SET_SPARSE_FILE_MODE()`, `ZSTD_SPARSE_DEFAULT`, `ZSTD_START_SYMBOLLIST_FRAME`, `ZSTD_SETPRIORITY_SUPPORT`, and `ZSTD_NANOSLEEP_SUPPORT`. On Windows, `IS_CONSOLE()` checks both `_isatty()` and `GetConsoleMode()`.

## Control Flow, State, and Persistence

There is no runtime persistence except inline Windows console detection. Most behavior is decided at preprocessing time, so the same source compiles different code paths depending on OS and feature-test macros.

## Dependencies and Integration Points

It conditionally includes `unistd.h`, `stdio.h`, `io.h`, `fcntl.h`, `windows.h`, and `winioctl.h`. Nearly every zstd CLI support module includes it before platform-sensitive system headers.

## Risks and Test Signals

Feature detection can accidentally expose or hide APIs on unusual libc/OS combinations. Tests should cover Windows console behavior, POSIX large-file seeking, macOS sparse default, non-POSIX fallback builds, and build matrices for Linux, BSD, MinGW, MSVC, Cygwin, and AIX-like targets.
