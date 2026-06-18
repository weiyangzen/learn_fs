# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/syscall.h

## Purpose

This header declares `XPlatform::Syscall`, libhdfspp's cross-platform wrapper for a small set of OS-level functions.

## Important APIs, types, and functions

The public static methods are `WriteToStdout(std::string)`, `WriteToStdout(const char*)`, `FnMatch()`, `ClearBufferSafely()`, `StringCompareIgnoreCase()`, `CreateAndOpenTempFile()`, `CloseFile()`, and `CreateTempDir()`. `WriteToStdoutImpl()` is private and implemented per platform.

## Control flow, state, and persistence

The header defines no state. Implementations invoke POSIX or Windows APIs. Temporary file and directory methods mutate the caller-provided pattern vector by appending a null terminator and replacing trailing `X` placeholders through platform APIs; created files/directories persist until callers remove them.

## Dependencies and integration points

The class is used by SASL auth method parsing, tests, temporary-file utilities, mini DFS helpers, and C wrappers. It also helps keep sensitive buffers clear through `ClearBufferSafely()`.

## Risks and test signals

Security-sensitive code depends on `ClearBufferSafely()` not being optimized away. Temp-file behavior must avoid races, especially on Windows where `_mktemp_s` plus exclusive open is used. Tests should cover fnmatch semantics, case-insensitive comparisons, stdout return values, temp path mutation, file descriptor closure, and secure buffer clearing on supported platforms.
