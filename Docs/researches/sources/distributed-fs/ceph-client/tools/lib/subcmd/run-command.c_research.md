# sources/distributed-fs/ceph-client/tools/lib/subcmd/run-command.c

Purpose: Provides child process execution helpers with optional stdin/stdout/stderr pipes, environment/working-directory setup, exec-subcmd support, and blocking/nonblocking finish checks.

Important APIs/types/functions: Public APIs are `start_command()`, `check_if_command_finished()`, `finish_command()`, `run_command()`, and `run_command_v_opt()`. Internal helpers include `close_pair()`, `dup_devnull()`, `wait_or_whine()`, and `prepare_run_command_v_opt()`.

Control flow: `start_command()` allocates requested pipes, forks, sets up child stdio, changes directory, applies environment entries or unsets variables, runs optional preexec/no-exec callback, then calls `execv_cmd()` or `execvp()`. The parent closes opposite pipe ends and returns. `finish_command()` waits and normalizes exit status to 0 or negative error/code. Linux `check_if_command_finished()` reads `/proc/<pid>/status` to avoid reaping early.

State and persistence: Mutates `struct child_process` fields (`pid`, FDs, `finished`, `finish_result`). Child process state is external to the library. No files are persisted.

Dependencies/integration: Uses POSIX fork/pipe/dup2/exec/wait, `/proc` on Linux, `str_error_r()`, `exec-cmd.c`, and `subcmd-util.h`.

Risks: Pipe/file descriptor ownership is subtle; passed FDs are closed even on some error paths as documented. `dup_devnull()` does not check `open()` failure. Environment handling mutates the child process before exec. Nonblocking finish on Linux relies on `/proc`, so behavior differs across platforms. Exit code 127 is mapped to exec failure, which may conflate real child exit 127.

Test signals: Test FD redirection combinations, no-stdin/stdout/stderr, stdout-to-stderr, working-directory failure, environment set/unset, preexec/no-exec callbacks, exec failure, signal exit, nonblocking status, and repeated `finish_command()`.
