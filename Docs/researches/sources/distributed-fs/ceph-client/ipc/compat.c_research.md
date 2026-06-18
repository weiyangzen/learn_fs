# sources/distributed-fs/ceph-client/ipc/compat.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/compat.c` converts 32-bit compatibility IPC permission structures to and from native kernel `ipc64_perm` structures. The source was read as a complete 82-line file.

## Important APIs, Types, and Functions

`get_compat_ipc64_perm()` and `get_compat_ipc_perm()` copy compat permission structures from userspace into `struct ipc64_perm`, preserving uid, gid, and mode. `to_compat_ipc64_perm()` fills the modern compat layout with key, uid/gid, creator uid/gid, mode, and sequence. `to_compat_ipc_perm()` fills the old compat layout and uses `SET_UID()`/`SET_GID()` conversions for legacy narrow uid/gid fields.

## Control Flow

All functions are small conversion helpers. The `get_*` functions first `copy_from_user()` into a stack local and return `-EFAULT` on bad user memory. The `to_*` functions populate caller-provided kernel-side compat structs before the caller copies them to userspace.

## State and Persistence Behavior

No state is stored. These helpers translate syscall arguments/results for message, semaphore, and shared-memory `IPC_SET`/`IPC_STAT` compatibility paths.

## Dependencies and Integration Points

The file depends on compat ABI definitions, highuid conversion helpers, user-copy APIs, and IPC utility declarations. It is called from compat implementations in `msg.c`, `sem.c`, and `shm.c`, and indirectly from the old compat `sys_ipc` multiplexer.

## Risks and Edge Cases

The compatibility ABI is sensitive to structure layout, uid/gid width, and time/sequence field placement. Bad copies must never partially update live permissions. Old ABI conversion can truncate ids, so tests need to distinguish legacy behavior from IPC_64 behavior.

## Test Signals

Compat syscall tests should exercise `IPC_SET` and `IPC_STAT`/`*_STAT` for msg, sem, and shm using both old and IPC_64 command versions, invalid user pointers, high uid/gid values, and 32-bit userlands on 64-bit kernels.
