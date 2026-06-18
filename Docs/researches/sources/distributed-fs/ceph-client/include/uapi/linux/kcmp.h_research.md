# sources/distributed-fs/ceph-client/include/uapi/linux/kcmp.h

## Purpose
`kcmp.h` defines the comparison type enum and epoll-slot structure for the `kcmp` syscall, which compares whether two processes share selected kernel resources.

## Important APIs, Types, and Functions
`enum kcmp_type` includes file table, VM, files, fs, sighand, io context, System V sem undo, epoll target file, and file comparison cases. `struct kcmp_epoll_slot` identifies an epoll file descriptor, target file descriptor, target fd number, and epoll event offset.

## Control Flow
Userspace invokes `kcmp(pid1, pid2, type, idx1, idx2)` with optional pointer-like arguments for epoll comparison. The kernel checks process visibility and compares internal object pointers or resource identities.

## State and Persistence
No state is created. Results reflect current process resource sharing and can change immediately after the syscall due to process activity.

## Dependencies and Integration Points
It includes `<linux/types.h>`. Integration points include checkpoint/restore tooling, process inspection, epoll internals, and security ptrace access checks.

## Risks and Test Signals
Tests should cover permission failures, races with closing fds, each comparison type, epoll slot matching, and behavior across pid/user namespaces. ABI risk is low but pointer-identity semantics are subtle.
