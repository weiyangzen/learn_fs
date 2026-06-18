# File Research: sources/block-storage/util-linux/sys-utils/ipcs.c

Purpose: Implements `ipcs(1)`, displaying System V IPC status, limits, ownership, timestamps, PIDs, and detailed resource data.

Core behavior:
- Selects resource classes with `--queues`, `--shmems`, `--semaphores`, or defaults to all.
- Selects output forms: default listings, `--time`, `--pid`, `--creator`, `--limits`, `--summary`, and specific `--id` detail mode.
- Supports byte and human-readable size output using `ipc_print_size()`.
- For shared memory, prints limits/status, standard listings including status flags (`dest`, `locked`), creator/owner, attach/detach/change times, PIDs, and detailed id records.
- For semaphores, prints limits/status, array listings, creator/owner, operation/change times, and per-semaphore values/wait counts/PIDs in id detail mode.
- For message queues, prints limits/status, queue listings, creator/owner, send/receive/change times, PIDs, and detailed id records including queue byte limits.

Dependencies and integration:
- Uses data collection and formatting helpers from `ipcutils.c`/`ipcutils.h`.
- Uses `timeutils.h` for ctime buffer sizing and util-linux parsing/NLS helpers.

Risks and edge cases:
- `--id` requires exactly one resource class; without `--id`, no class means all classes.
- `ctime64()` casts int64-backed procfs timestamps to `time_t *`, matching the file comment's assumption but depending on local `time_t` representation compatibility.
- POSIX IPC structures exist in `ipcutils.h`, but this `ipcs.c` implementation displays System V IPC only.
