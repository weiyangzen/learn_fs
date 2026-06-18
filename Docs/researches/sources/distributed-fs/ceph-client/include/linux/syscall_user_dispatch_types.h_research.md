<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h -->
# sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h

## Purpose

`syscall_user_dispatch_types.h` defines the per-task storage shape for syscall user dispatch. It is separated from the API header so low-level task/thread structures can include the type without pulling in the full control API.

## Important APIs, types, and functions

With `CONFIG_GENERIC_ENTRY`, `struct syscall_user_dispatch` contains a userspace `selector`, an allowed `offset`, allowed `len`, and `on_dispatch` recursion/dispatch-state flag. Without generic entry, the struct is empty.

## Control flow

The type is read by syscall entry code and written by configuration code declared in `syscall_user_dispatch.h`. `on_dispatch` helps distinguish active dispatch handling from normal syscall execution.

## State and persistence behavior

The struct is per-task state. The selector pointer targets userspace memory and the offset/length range defines a persistent allowed syscall region until reconfigured.

## Dependencies and integration points

It depends on `linux/types.h` and integrates with task structs, generic syscall entry, and syscall user dispatch configuration APIs.

## Risks and test signals

Risks include empty-struct layout assumptions when generic entry is disabled, invalid userspace selector pointers, offset/length overflow, and recursion state leaks. Tests should cover structure availability in both config modes, range boundary checks, selector fault handling, and dispatch recursion state clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch_types.h -->
