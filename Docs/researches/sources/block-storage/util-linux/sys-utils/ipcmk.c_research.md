# File Research: sources/block-storage/util-linux/sys-utils/ipcmk.c

Purpose: Implements `ipcmk(1)`, a utility for creating ad-hoc System V and POSIX IPC resources.

Core behavior:
- Creates System V shared memory (`shmget`), message queues (`msgget`), and semaphore arrays (`semget`) using random keys from util-linux random helpers.
- Creates POSIX shared memory (`shm_open` plus `ftruncate`), POSIX message queues (`mq_open`), and POSIX semaphores (`sem_open`) when the relevant headers/features are available.
- Parses resource size/count, octal permissions, and POSIX resource names; POSIX IPC creation requires `--name`.
- Prints the created System V id or POSIX name on success.

Dependencies and integration:
- Uses `randutils.h` for random keys, `strutils.h` for size/integer parsing, and feature guards for `mqueue.h`, `semaphore.h`, and `sys/mman.h`.

Risks and edge cases:
- Multiple creation options can be combined; a single `size`, `nsems`, `permission`, and `name` state is reused according to parsed options.
- POSIX fallbacks emit "not supported" warnings and fail cleanly when headers/features are unavailable.
- System V resources use random keys with `IPC_CREAT` but not `IPC_EXCL`, so an unlikely key collision could attach to an existing resource type rather than force uniqueness.
