# sources/distributed-fs/glusterfs/libglusterfs/src/run.c

## Purpose

`run.c` implements Gluster's `runner_t` subprocess helper using `posix_spawnp()`. It builds an argv vector, supports stdout/stderr/stdin pipe or fd redirection, closes unintended file descriptors in the child, reports spawn/exec setup failures, and offers convenience wrappers for blocking, nonblocking, reusable, and varargs command execution.

## Important APIs, Types, and Functions

The main API is `runinit()`, `runner_add_arg()`, `runner_add_args()`, `runner_argprintf()`, `runner_log()`, `runner_redir()`, `runner_chio()`, `runner_start()`, `runner_end_reuse()`, `runner_end()`, `runner_run()`, `runner_run_nowait()`, `runner_run_reuse()`, and `runcmd()`. `runner_t` owns dynamic `argv`, a remembered allocation error `runerr`, child pid `chpid`, target redirection fds in `chfd`, and parent-side `FILE *` streams in `chio`.

## Control Flow and Data Flow

Callers initialize a runner, append duplicated arguments, optionally mark fd 1 or 2 as `RUN_PIPE` or redirect to an existing fd, and then start or run. `runner_start()` creates an error-report pipe with close-on-exec behavior, creates requested stdio pipes, builds `posix_spawn_file_actions_t` entries for closing parent pipe ends, duping requested child fds, and closing all other fds through `close_fds_except_custom()` plus `closer_posix_spawnp()`. It clears the child signal mask with spawn attributes and invokes `posix_spawnp()`. Parent-side flow closes child pipe ends, reads the error pipe to detect setup/exec-style failure, and leaves parent `FILE *` streams open for callers.

`runner_end_reuse()` waits for the child, closes pipe streams, and returns the negated exit status or raw wait status. `runner_end()` additionally frees every argv string and the argv array and closes redirection fds. `runner_run_nowait()` forks a detached launcher that calls `runner_start()` after `setsid()` and then lets the original runner clean up.

## State and Persistence Behavior

State is process-local. The only lasting effects are whatever the spawned command does and any redirected output written to files supplied by callers. Arguments are heap-owned by the runner after insertion and freed by `runner_end()`. Pipe streams persist until `runner_end*()` is called. Child process lifetime is tracked by `chpid`.

## Dependencies and Integration Points

This file depends on POSIX spawn, pipes, fd actions, Gluster memory helpers, logging, `close_fds_except_custom()`, and syscall wrappers for read/write/close. It integrates with Gluster management and utility code that needs controlled external command execution without exposing inherited daemon fds.

## Risks and Edge Cases

`runner_redir()` only accepts fd 1 or 2 despite the array covering 0..2, so stdin pipe use is not exposed by the assertion path. Several early error paths in `runner_start()` return without destroying initialized spawn objects or closing all already-created fds, so leak tests matter. The parent writes its own `errno` to the close-on-exec pipe after successful spawn; with `posix_spawnp()` this differs from the fork implementation's child-side exec failure channel and should be validated on target platforms. `runner_run_nowait()` has two process layers and returns through normal cleanup, so process-parenting behavior is easy to misinterpret.

## Test Signals

The built-in `RUN_DO_DEMO` block exercises argv growth, logging, pipes, missing commands, and file redirection. Automated tests should add fd-leak checks, redirection to existing fds, `RUN_PIPE` output reads, command-not-found behavior, nonzero exit status mapping, and nowait process reaping behavior. Platform tests should compare this implementation against `run_fork.c` where `posix_spawn()` is unavailable or broken.
