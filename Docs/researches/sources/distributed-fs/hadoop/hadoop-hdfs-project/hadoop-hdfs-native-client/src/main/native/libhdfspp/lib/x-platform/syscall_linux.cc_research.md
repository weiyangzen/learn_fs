# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/syscall_linux.cc

## Purpose

This file implements `XPlatform::Syscall` for POSIX-like systems.

## Important APIs, types, and functions

It implements stdout writes using `write(1, ...)`, wildcard matching with `fnmatch()`, buffer clearing with `explicit_bzero()` when available or `bzero()` otherwise, case-insensitive comparison with `strcasecmp()`, temporary files with `mkstemp()`, closing with `close()`, and temporary directories with `mkdtemp()`.

## Control flow, state, and persistence

`WriteToStdoutImpl()` writes the exact string length and reports success only if all bytes are written in one call. `CreateAndOpenTempFile()` and `CreateTempDir()` append a null terminator to the pattern vector before calling the POSIX function; the mutated vector retains the generated path. State is OS state: file descriptors and created filesystem entries.

## Dependencies and integration points

It includes `<fnmatch.h>`, `<strings.h>`, `<unistd.h>`, `<cstring>`, and the x-platform `types.h` for `ssize_t`. It is selected by CMake for non-Windows builds and used by native client tests and C wrappers.

## Risks and test signals

Partial stdout writes are treated as failure without retry, which is acceptable for short diagnostic strings but not a streaming abstraction. The fallback `bzero()` may still be optimized depending on platform guarantees, so `HAVE_EXPLICIT_BZERO` matters for sensitive data. Tests should cover temp creation, close errors, fnmatch wildcards, case-insensitive equality, and buffer clearing with sanitizers if available.
