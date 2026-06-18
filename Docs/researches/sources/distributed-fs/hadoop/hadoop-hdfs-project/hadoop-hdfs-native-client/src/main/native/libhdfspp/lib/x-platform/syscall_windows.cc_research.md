# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/syscall_windows.cc

## Purpose

This file implements `XPlatform::Syscall` for Windows.

## Important APIs, types, and functions

It implements stdout writes with `GetStdHandle()` and `WriteFile()`, wildcard matching with `PathMatchSpecA()`, secure clearing with `SecureZeroMemory()`, case-insensitive comparison with `_stricmp()`, temp-file creation using `_mktemp_s()` followed by `_sopen_s(..., _O_CREAT | _O_EXCL, _SH_DENYNO, ...)`, close with `_close()`, and temp-directory creation with `_mkdir()`.

## Control flow, state, and persistence

Methods clear `errno` via `_set_errno(0)` before temp creation. Temp file creation first generates a unique name, then opens it exclusively to avoid overwriting an existing file. Temp directory creation similarly generates a name and creates the directory. Created filesystem entries and file descriptors outlive the wrapper call until caller cleanup.

## Dependencies and integration points

The implementation depends on Windows headers, Shlwapi, CRT file APIs, and `syscall.h`. CMake selects this file when `CMAKE_SYSTEM_NAME` is Windows. It supports libhdfspp tools and tests that otherwise assume POSIX-like behavior.

## Risks and test signals

`_mktemp_s()` name generation plus later `_mkdir()` for directories can still race if another process creates the directory first, though file creation uses exclusive open. `PathMatchSpecA()` wildcard semantics may not exactly match POSIX `fnmatch()`. Windows CI should verify stdout, wildcard matching, temp file and directory creation, close behavior, and secure buffer clearing.
