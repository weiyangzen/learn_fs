# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/types.h

## Purpose

This header normalizes `ssize_t` availability for Windows and non-Windows builds.

## Important APIs, types, and functions

On `_WIN64`, it typedefs `ssize_t` as `long int`; on `_WIN32`, it typedefs `ssize_t` as `int`; otherwise it includes `<sys/types.h>` and uses the platform definition.

## Control flow, state, and persistence

There is no runtime behavior. The file only affects type availability at compile time.

## Dependencies and integration points

It is used by the POSIX syscall implementation and any code that wants a signed byte-count type without sprinkling platform checks through the codebase.

## Risks and test signals

The `_WIN64` choice of `long int` follows this code's assumptions but Windows `long` remains 32-bit under LLP64, so it may not represent all pointer-sized counts. Tests should focus on compilation and typical write lengths; any future large-buffer APIs should use more explicit fixed-width types or platform-native signed sizes.
