# sources/distributed-fs/glusterfs/libglusterfs/src/glusterfs/run.h

Purpose: `run.h` declares the `runner_t` helper for constructing and executing child processes with argument accumulation, logging, and stdio redirection.

Important APIs and types: `runner_t` stores argv, argv length, deferred error, child pid, child file descriptors, and child `FILE *` streams. APIs include `runinit`, `runner_add_arg`, `runner_add_args`, `runner_argprintf`, `runner_log`, `runner_redir`, `runner_start`, `runner_end`, reusable variants, `runner_run`, `runner_run_nowait`, and `runcmd`. `RUN_PIPE` requests a parent-readable pipe.

Control flow and state: callers initialize, add arguments, optionally configure redirections, start the child, interact with child pipes, and end/reap/free. Error handling is deferred during argument construction and surfaced during start/run.

Dependencies and integration: uses logging types and is a safer abstraction for LVM/tool invocations than ad hoc `system()`. It interacts with `syscall.h` wrappers and command path headers such as `lvm-defaults.h`.

Risks: vararg argument sequences must be NULL-terminated. Redirection ownership closes target fds in `runner_end`, so callers must dup fds they need. `runner_run_nowait` assumes success and can hide exec failures. Child-pipe consumers must avoid deadlocks.

Test signals: spawn success/failure, argument quoting/no-shell behavior, pipe redirection, fd ownership, reusable runner paths, nowait behavior, and signal/waitpid status decoding should be covered.
