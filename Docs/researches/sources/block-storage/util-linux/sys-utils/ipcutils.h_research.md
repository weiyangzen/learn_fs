# File Research: sources/block-storage/util-linux/sys-utils/ipcutils.h

Purpose: Header for shared IPC compatibility definitions, data structures, and helper APIs used by `ipcs`, `ipcrm`, and related IPC utilities.

Core contents:
- Includes System V IPC, POSIX mqueue/semaphore, passwd/group, and standard type headers under feature guards.
- Supplies fallback definitions for `SHM_DEST`, `SHM_LOCKED`, `MSG_STAT/INFO`, `SHM_STAT/INFO`, `SEM_STAT/INFO`, `IPC_INFO`, `struct shm_info`, and `union semun` where libc/kernel headers do not expose them.
- Defines the `KEY` macro abstraction for glibc `ipc_perm.__key` versus older `key`.
- Defines output units, `struct ipc_limits`, common `struct ipc_stat`, and typed linked-list records for System V shared memory/semaphore/message queues plus POSIX shared memory/semaphore/message queues.
- Declares limit, enumeration, free, permission-printing, and size-printing functions.

Dependencies and integration:
- Central contract for `ipcutils.c`, `ipcs.c`, and `ipcrm.c`.
- Encodes portability glue for older libc/kernel header combinations.

Risks and edge cases:
- Structures mirror kernel/procfs concepts and comments cite kernel internal structures; field availability and width assumptions must stay aligned with parser code in `ipcutils.c`.
