# sources/distributed-fs/ceph-client/tools/include/nolibc/sys/wait.h

## Purpose
Provides child-process wait wrappers and wait-status decoding for nolibc.

## APIs, Types, and Functions
Defines `_sys_waitid`, `waitid`, `waitpid`, and `wait`. Status macros such as `WIFEXITED` and `WEXITSTATUS` are supplied by `types.h`.

## Control Flow, State, and Persistence
`waitpid()` uses `wait4` when available or emulates through `waitid`, translating `siginfo_t` into traditional status words. `wait()` delegates to `waitpid(-1, ...)`. Persistent state is kernel child-process state consumed by wait operations.

## Dependencies and Integration
Depends on `../arch.h`, `../types.h`, `../sys.h`, and Linux wait/signal UAPI. It integrates with `fork`/`vfork` users and process-control tests.

## Risks and Test Signals
Risks include status-word emulation mistakes, option support differences, rusage omission in public `waitid`, and child reaping races in callers. Test signals are child exit/signal/stop/continue cases, `WNOHANG`, invalid pid/options, and architecture paths with and without native `wait4`.
