<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls_api.h -->
# sources/distributed-fs/ceph-client/include/linux/syscalls_api.h

## Purpose

`syscalls_api.h` is a one-line include shim for `linux/syscalls.h`. It offers an alternate API-facing include path without defining independent syscall symbols.

## Important APIs, types, and functions

All visible APIs come from `syscalls.h`: syscall definition macros, tracing metadata macros, compat aliases, and syscall prototypes.

## Control flow

There is no local control flow. Preprocessing immediately includes `syscalls.h`.

## State and persistence behavior

No state is owned here. Static metadata and ABI behavior are inherited from `syscalls.h`.

## Dependencies and integration points

It depends directly on `linux/syscalls.h` and integrates as a compatibility or layering header for code that wants syscall declarations.

## Risks and test signals

Risks are limited to include layering ambiguity and accidental assumptions that this header narrows the syscall API. Tests are compile-time: consumers including `syscalls_api.h` should see the same declarations as `syscalls.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscalls_api.h -->
