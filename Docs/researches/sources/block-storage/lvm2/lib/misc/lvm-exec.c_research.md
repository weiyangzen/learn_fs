# File Research: sources/block-storage/lvm2/lib/misc/lvm-exec.c

This file implements no-shell external command execution and pipe capture helpers.

Main entry points:
- `exec_cmd()` forks, optionally syncs local device names, logs arguments, resets child logging/locking, calls `execvp()`, waits, and returns exit status.
- `pipe_open()` forks a child whose stdout is connected to a pipe and returns a `FILE *` reader.
- `pipe_close()` closes the stream and waits for the child.
- `prepare_exec_args()` appends configured option strings to an argv array.

Implementation details:
- `_verbose_args()` renders argv for logging.
- `_reopen_fd_to_null()` safely redirects a controlled fd to `/dev/null`.
- Child process uses `execvp()` directly, not a shell.
- `sync_needed` calls `sync_local_dev_names()` before execution where allowed.

Dependencies:
- Locking reset, device sync, command context config, signals/wait, and standard fork/exec APIs.

Correctness notes:
- `exec_cmd()` distinguishes abnormal exit, nonzero exit, and wait failure.
- `pipe_open()` closes unused pipe ends and kills/waits child if `fdopen()` fails.
- `prepare_exec_args()` enforces `DEFAULT_MAX_EXEC_ARGS` and string-only config values.

Risks:
- Child exits with `errno` after failed exec; only low 8 bits are preserved by process exit.
- `execvp()` searches `PATH`, so configured executable resolution matters.
