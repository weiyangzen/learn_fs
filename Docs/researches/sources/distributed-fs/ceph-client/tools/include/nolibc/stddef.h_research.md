# sources/distributed-fs/ceph-client/tools/include/nolibc/stddef.h

## Purpose
Provides minimal standard definitions for null pointers and member offsets.

## APIs, Types, and Functions
Defines `NULL` as `((void *)0)` and `offsetof(TYPE, FIELD)` through `__builtin_offsetof`.

## Control Flow, State, and Persistence
No runtime state exists. `offsetof` is compile-time expression support for structure layout calculations.

## Dependencies and Integration
Depends on compiler `__builtin_offsetof`. It integrates with `container_of` in `types.h` and layout-sensitive syscall structures.

## Risks and Test Signals
Risks are incomplete `<stddef.h>` compatibility, including missing `wchar_t` or `max_align_t`, and C++ null pointer expectations. Test signals are compile checks for `offsetof` on nested structs and consumers requiring only `NULL` and offsets.
