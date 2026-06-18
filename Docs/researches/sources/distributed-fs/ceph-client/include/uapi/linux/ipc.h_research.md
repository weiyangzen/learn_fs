# sources/distributed-fs/ceph-client/include/uapi/linux/ipc.h

## Purpose
`ipc.h` defines common System V IPC constants, permission metadata, control commands, and legacy multiplexing numbers shared by message queues, semaphores, and shared memory.

## Important APIs, Types, and Functions
`IPC_PRIVATE` identifies private keys. `struct ipc_perm` carries key, UID/GID, creator UID/GID, mode, and sequence fields. Control flags include `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, historical DIPC flags, and commands `IPC_RMID`, `IPC_SET`, `IPC_STAT`, and `IPC_INFO`. `IPC_OLD` and `IPC_64` identify old/new ABI variants. `struct ipc_kludge` supports legacy message receive arguments. `IPCCALL(version, op)` packs legacy multiplexed syscall operations.

## Control Flow
Userspace creates or finds IPC objects by key, then performs resource-specific syscalls that share this permission and command vocabulary. The kernel validates permissions, object existence, namespace membership, and versioned structure layout.

## State and Persistence
IPC objects persist in kernel IPC namespaces until removed, namespace teardown, or system reboot. Permission changes via `IPC_SET` mutate object metadata.

## Dependencies and Integration Points
The header includes `<linux/types.h>` and `<asm/ipcbuf.h>`. It integrates with SysV IPC syscalls, namespace accounting, permission checks, `ipcs`/`ipcrm`, and compatibility syscall paths.

## Risks and Test Signals
Tests should cover namespace isolation, old versus `IPC_64` layout handling, permission mutation, stale sequence IDs, and behavior of wait versus `IPC_NOWAIT`. Compatibility risk exists around UID/GID field widths and architecture-specific `ipcbuf` layout.
