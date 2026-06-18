# sources/distributed-fs/ceph-client/tools/include/linux/container_of.h

## Purpose

This header provides the kernel-style `container_of` macro for tools code.

## APIs, State, and Dependencies

If not already defined, `container_of(ptr, type, member)` captures the member pointer type and subtracts `offsetof(type, member)` from it to recover the containing structure pointer. There is no state.

## Risks and Test Signals

The macro requires a valid pointer to the named member and an included declaration of `offsetof`. Misuse with wrong types can produce invalid pointers despite the type check. Tests should compile representative intrusive-list or embedded-struct users and run pointer round-trip checks.
