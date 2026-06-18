# sources/distributed-fs/ceph-client/ipc/syscall.c

## Purpose

`sources/distributed-fs/ceph-client/ipc/syscall.c` implements the legacy `sys_ipc` multiplexed System V IPC syscall and old compat multiplexer variants for architectures that still request them. The source was read as a complete 211-line file.

## Important APIs, Types, and Functions

`ksys_ipc()` decodes the high-word IPC version and low-word operation, then dispatches to semaphore, message, and shared-memory helpers. `SYSCALL_DEFINE6(ipc)` exposes that path when `__ARCH_WANT_SYS_IPC` is set. Under compat support, `compat_ksys_ipc()` and `COMPAT_SYSCALL_DEFINE6(ipc)` do equivalent decoding for `CONFIG_ARCH_WANT_OLD_COMPAT_IPC`. `struct compat_ipc_kludge` mirrors the old message-receive kludge layout.

## Control Flow

The multiplexer switches on operations such as `SEMOP`, `SEMTIMEDOP`, `SEMGET`, `SEMCTL`, `MSGSND`, `MSGRCV`, `MSGGET`, `MSGCTL`, `SHMAT`, `SHMDT`, `SHMGET`, and `SHMCTL`. Older `MSGRCV` and `SHMAT` ABIs use kludge structs or out-parameters; newer variants pass direct pointers and values. Time handling dispatches to native timespec or compat old-timespec helpers depending on configuration.

## State and Persistence Behavior

This file owns no IPC objects. It only translates the old syscall ABI into calls that mutate message queues, semaphores, or shared-memory segments in the current IPC namespace.

## Dependencies and Integration Points

It integrates architecture syscall selection, SysV IPC helper functions from `msg.c`, `sem.c`, and `shm.c`, version parsing conventions, compat pointer conversion, old 32-bit time support, and shared-memory alignment constants such as `SHMLBA`/`COMPAT_SHMLBA`.

## Risks and Edge Cases

The risk is ABI compatibility. The multiplexer must preserve historical argument packing, including `SEMCTL` reading an indirect argument, old `MSGRCV` kludge handling, `SHMAT` returning an address through `third`, and rejecting unsupported version-1 `SHMAT`. Compat paths must reject negative ids/sizes where required and avoid truncating returned attach addresses incorrectly.

## Test Signals

Tests should run old `ipc()` syscall variants where supported for all SysV IPC families, including old and new `MSGRCV`, indirect `SEMCTL`, `SHMAT` out-address storage, invalid operation numbers, unsupported time configurations, and compat 32-bit userland behavior.
