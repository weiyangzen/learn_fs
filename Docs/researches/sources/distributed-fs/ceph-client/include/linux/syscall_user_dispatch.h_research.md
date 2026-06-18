<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h -->
# sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h

## Purpose

`syscall_user_dispatch.h` declares the kernel control interface for syscall user dispatch, a generic-entry feature that can redirect selected syscalls to userspace emulation based on configured address ranges and a userspace selector byte.

## Important APIs, types, and functions

When `CONFIG_GENERIC_ENTRY` is enabled, APIs are `set_syscall_user_dispatch()`, `clear_syscall_work_syscall_user_dispatch()`, `syscall_user_dispatch_get_config()`, and `syscall_user_dispatch_set_config()`. Disabled builds return `-EINVAL` or no-op. It includes `struct syscall_user_dispatch` from the companion types header.

## Control flow

Configuration paths set mode, allowed offset/length, and selector address on a task. Entry code checks syscall work flags and dispatch configuration before executing a syscall; clearing the work bit disables checks for the task. Get/set config functions support ptrace/prctl-style inspection and update.

## State and persistence behavior

Per-task state lives in thread/task structures through `struct syscall_user_dispatch`. The selector is a userspace pointer and must be accessed carefully. Configuration persists until changed, cleared, exec/reset by owning logic, or task exit.

## Dependencies and integration points

It depends on thread-info syscall work helpers, task structs, user pointers, and `syscall_user_dispatch_types.h`. It integrates with generic syscall entry, prctl/ptrace config paths, compatibility layers, and userspace emulators such as Wine-like runtimes.

## Risks and test signals

Risks include unsafe selector access, wrong allowed-region boundaries, failing to clear syscall work, ptrace size validation errors, and inconsistent behavior on architectures without generic entry. Tests should cover enable/disable, allowed and dispatched address ranges, selector toggling, get/set config ABI sizes, fork/exec semantics, signal/syscall restart interactions, and disabled-config stubs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/syscall_user_dispatch.h -->
