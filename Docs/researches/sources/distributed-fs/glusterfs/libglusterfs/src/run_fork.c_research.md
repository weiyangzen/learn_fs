# sources/distributed-fs/glusterfs/libglusterfs/src/run_fork.c

## Purpose

`run_fork.c` is the legacy fork/exec implementation of the same `runner_t` API provided by `run.c`, kept for platforms with broken or old `posix_spawn()` support. It constructs command arguments, manages optional stdio pipes or fd redirection, closes inherited descriptors in the child, and reports `execvp()` failures through a close-on-exec pipe.

## Important APIs, Types, and Functions

The public API matches `run.c`: `runinit()`, `runner_chio()`, `runner_add_arg()`, `runner_add_args()`, `runner_argprintf()`, `runner_log()`, `runner_redir()`, `runner_start()`, `runner_end_reuse()`, `runner_end()`, `runner_run()`, `runner_run_nowait()`, `runner_run_reuse()`, and `runcmd()`. Under standalone builds it provides `close_fds_except()`.

## Control Flow and Data Flow

Setup mirrors the spawn version until `runner_start()`. It creates the error pipe, marks the writer close-on-exec, creates requested stdio pipes, then forks. The child closes parent pipe ends, performs `dup2()` for each requested pipe or file redirection, closes all fds except standard fds and the error pipe writer, clears the signal mask, and calls `execvp()`. If setup or exec fails, the child writes `errno` to the error pipe and exits. The parent closes child pipe ends and reads the error pipe; EOF means exec succeeded.

End and convenience flows match `run.c`: wait and close streams in `runner_end_reuse()`, free argv and close redirect fds in `runner_end()`, and wrap initialization/varargs in `runcmd()`.

## State and Persistence Behavior

The runner owns heap-duplicated argv entries and parent-side pipe streams. Persistent effects are external to the helper and come from the executed command. The error pipe is transient state used to distinguish child setup failure from successful exec.

## Dependencies and Integration Points

The file depends on `fork()`, `execvp()`, POSIX pipes, `dup2()`, waitpid, Gluster logging/memory helpers, and syscall wrappers. It is selected for legacy platforms and should behave consistently with the `posix_spawnp()` implementation from a caller's perspective.

## Risks and Edge Cases

Forking a multithreaded daemon is riskier than `posix_spawn()` because only async-signal-safe work should be done in the child before exec; this child does descriptor and signal-mask work. The fd-closing loop depends on `RLIMIT_NOFILE` in standalone mode and on Gluster's implementation otherwise. `runner_redir()` accepts only fd 1 or 2. Error and cleanup paths can leak temporary fds if pipe creation or `fdopen()` partially succeeds. Return values are negative exit statuses, which can surprise code expecting raw wait status.

## Test Signals

Tests should be shared with `run.c` to enforce API parity: successful commands, command-not-found errno, argv growth, stdout/stderr pipe reads, output redirection, nonzero exit status, reuse after `runner_run_reuse()`, and fd inheritance checks. Threaded daemon tests should specifically watch for deadlock or unsafe behavior around fork.
