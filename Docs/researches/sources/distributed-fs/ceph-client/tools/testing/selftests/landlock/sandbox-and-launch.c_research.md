# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/sandbox-and-launch.c

## Purpose

`sandbox-and-launch.c` is a helper executable used by mount/layout Landlock tests. It sandboxes itself with `LANDLOCK_SCOPE_SIGNAL`, reports readiness through a pipe, waits for the parent test to exercise mount behavior, and then `execve()`s another supplied program with the pipe arguments shifted forward.

## Important APIs, Types, and Functions

It uses `struct landlock_ruleset_attr.scoped`, `landlock_create_ruleset()`, `landlock_restrict_self()`, `prctl(PR_SET_NO_NEW_PRIVS)`, `write()`, `read()`, `close()`, `atoi()`, and `execve()`. `wrappers.h` supplies direct syscall wrappers for Landlock on systems whose libc headers do not expose them.

## Control Flow and State

The program expects exactly three logical arguments after its name: target binary and two pipe file descriptors. It creates the scoped domain, closes the ruleset FD, writes one byte to the child pipe, blocks on the parent pipe, mutates `argv` in place, and replaces itself with the target executable. Persistent state is only the process's Landlock domain and inherited open pipe descriptors.

## Dependencies and Integration Points

It integrates with Landlock filesystem tests that need a process to cross an exec boundary after entering a signal-scoped sandbox. It depends on valid inherited file descriptors and on the parent having already set up the expected synchronization protocol.

## Risks and Test Signals

Risks are argument-order mistakes, leaked ruleset FDs, lost synchronization bytes, and accidental environment inheritance expectations because `execve()` passes `NULL` environment. Useful signals are error messages on failed Landlock setup, pipe read/write failures, and the downstream target executing only after the parent's synchronization byte.
