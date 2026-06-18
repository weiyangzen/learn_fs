# File Research: sources/block-storage/lvm2/lib/misc/lvm-exec.h

This header declares external command helpers.

APIs:
- `exec_cmd(struct cmd_context *, const char *const argv[], int *rstatus, int sync_needed)`.
- `struct pipe_data { FILE *fp; pid_t pid; }`.
- `pipe_open()`, `pipe_close()`.
- `prepare_exec_args()`.

Notes:
- Comments warn that device synchronization cannot be done inside activation context.
- Pipe helper is explicitly popen-like but does not run a shell.

Dependencies:
- Includes `lib/misc/lib.h` and forward-declares `cmd_context`.
