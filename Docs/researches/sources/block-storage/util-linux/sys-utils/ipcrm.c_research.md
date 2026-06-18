# File Research: sources/block-storage/util-linux/sys-utils/ipcrm.c

Purpose: Implements `ipcrm(1)`, removing System V and POSIX IPC resources by id, key, name, or whole category.

Core behavior:
- Supports modern options for shared memory, message queues, semaphores by id/key, and POSIX shared memory/message queues/semaphores by name.
- Retains deprecated syntax `ipcrm shm|msg|sem <id>...`.
- Converts System V keys to ids with `shmget`, `msgget`, or `semget`, rejecting `IPC_PRIVATE`.
- Removes System V resources with `shmctl(IPC_RMID)`, `msgctl(IPC_RMID)`, or `semctl(IPC_RMID)`.
- Removes POSIX resources with `shm_unlink`, `mq_unlink`, and `sem_unlink` under feature guards.
- `--all[=shm|pshm|msg|pmsg|sem|psem]` enumerates each resource class and removes discovered resources.

Important implementation details:
- System V "remove all" uses kernel enumeration via `SHM_INFO/SHM_STAT`, `SEM_INFO/SEM_STAT`, and `MSG_INFO/MSG_STAT`.
- POSIX "remove all" relies on `ipcutils` enumeration functions over `/dev/shm` and `/dev/mqueue`.
- Removal errors are accumulated; the command exits failure if any requested removal fails.

Dependencies and integration:
- Depends on `ipcutils.h` for POSIX enumeration structures and fallback compatibility definitions.
- Shares POSIX IPC support additions with `ipcmk.c` and `ipcutils.c`.

Risks and edge cases:
- `--all` is broad and destructive by design; filtering by category is supported but not by owner.
- Error strings distinguish invalid/permission/already-removed ids and keys for System V resources.
