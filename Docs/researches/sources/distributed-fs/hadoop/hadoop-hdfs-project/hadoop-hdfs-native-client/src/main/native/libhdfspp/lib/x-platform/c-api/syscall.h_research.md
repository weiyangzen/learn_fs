# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-native-client/src/main/native/libhdfspp/lib/x-platform/c-api/syscall.h

## Purpose

This header declares the C-callable syscall wrappers exported by the x-platform C API.

## Important APIs, types, and functions

The declarations are `x_platform_syscall_write_to_stdout(const char*)`, `x_platform_syscall_create_and_open_temp_file(char*, size_t)`, and `x_platform_syscall_close_file(int)`. They expose stdout writing, `mkstemp`-style temporary file creation, and file-descriptor close operations.

## Control flow, state, and persistence

The header has no runtime behavior. The implementation owns all OS interaction. State visible to callers is the returned file descriptor and the possibly modified temporary path buffer.

## Dependencies and integration points

It is intended for C consumers in libhdfspp bindings and tests. The declarations are simple enough to include from C translation units, though the header relies on `size_t` being available from included context or toolchain defaults.

## Risks and test signals

The main risk is header completeness: strict C consumers may need an explicit `<stddef.h>` include for `size_t`. ABI tests should ensure C and C++ translation units agree on return types and that callers can link against `x_platform_obj_c_api`.
