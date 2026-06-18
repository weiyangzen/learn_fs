# File Research: sources/block-storage/util-linux/sys-utils/ipcutils.c

Purpose: Shared IPC data collection and formatting library for `ipcs` and `ipcrm`, covering System V IPC and newer POSIX IPC enumeration support.

Core behavior:
- Reads System V IPC limits from procfs paths when available, falling back to `msgctl(IPC_INFO)`, `semctl(IPC_INFO)`, or `shmctl(IPC_INFO)`.
- Collects shared memory, semaphore, and message queue records from `/proc/sysvipc/*` when available, falling back to kernel enumeration through `*_INFO` and `*_STAT`.
- For a specific semaphore id, retrieves each semaphore element's value, wait-for-increase count, wait-for-zero count, and last-operation PID.
- Enumerates POSIX shared memory and POSIX semaphores from `/dev/shm`, distinguishing semaphore entries by the `sem.` prefix.
- Enumerates POSIX message queues from `/dev/mqueue`, reading queue byte usage from the queue filesystem entry and current message count through `mq_getattr()`.
- Provides free functions for linked-list result structures and common printers for permissions and sizes.

Important implementation details:
- The System V list representation uses a sentinel-like extra allocated node; callers iterate until `next == NULL`.
- `ipc_print_size()` supports default bytes, kilobytes, and human output with configurable width and label style.
- POSIX message queue names are normalized with a leading `/` before `mq_open()`/comparison.

Dependencies and integration:
- Uses `pathnames.h` procfs and devfs constants, `path.h` read helpers, `xalloc.h`, `strutils.h`, and POSIX/System V IPC headers exposed through `ipcutils.h`.
- Serves `ipcs.c` for display and `ipcrm.c` for `--all` POSIX removal.

Risks and edge cases:
- Several POSIX result free functions free list nodes but not allocated name strings, so enumeration can leak per-entry names in long-running callers; current CLI tools are short-lived.
- The POSIX message queue allocator uses `sizeof(struct msg_data)` for a `struct posix_msg_data` pointer in the initial allocation, which overallocates but is type-inconsistent.
- Fallback paths assign `cgid` from `cuid` in shared memory and semaphore fallback records, which appears inconsistent with the procfs path and likely loses creator group information.
- Delta/list consumers assume stable procfs parsing formats, with partial parsing lines skipped.
