# File Research: sources/block-storage/util-linux/sys-utils/lsipc.c

`lsipc.c` implements `lsipc(1)`, a flexible System V and POSIX IPC reporting utility.

Key behavior:
- Supports System V shared memory, message queues, semaphores, and global IPC limits.
- Supports POSIX shared memory, POSIX message queues, and POSIX semaphores.
- Defines one shared column table with generic, POSIX, message, shared-memory, semaphore, summary, and POSIX-semaphore-specific columns.
- Enforces resource-specific column applicability via global `LOWER`/`UPPER` bounds.
- Supports output modes: list, pretty, export, newline, raw, and JSON.
- Supports owner/creator columns, time columns, numeric permissions, byte sizes, shell-safe names, no headings, and no truncation.
- Pretty mode prints a single resource as key/value rows and can include a subtable of semaphore elements.
- Uses `ipcutils` helpers to collect IPC data and limits.
- Uses `pid_get_cmdline()` for creator/last-user command display.
- Uses `make_time()` for short, full, and ISO timestamps.

Important dependencies:
- `ipcutils.h` and related IPC helper implementations for System V/POSIX enumeration.
- `libsmartcols` for all tabular and JSON output.
- passwd/group lookup APIs for user/group name resolution.
- util-linux time, string, parsing, and option-exclusion helpers.

Risk notes:
- Option exclusivity is complex because resource selection, global mode, ID/name lookup, and output modes interact.
- `LOWER`/`UPPER` are mutable globals set by selected resource mode; custom columns rely on them being set correctly.
- Some POSIX global reporting is compiled out when message queue headers are unavailable.
- There appears to be a likely typo in the System V shared-memory `COL_CGID` case: it prints `p->shm_perm.cuid` instead of `p->shm_perm.cgid`.
