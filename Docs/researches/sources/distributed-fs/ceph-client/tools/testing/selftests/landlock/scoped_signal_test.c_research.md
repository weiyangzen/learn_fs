# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/scoped_signal_test.c

## Purpose

`scoped_signal_test.c` validates `LANDLOCK_SCOPE_SIGNAL` for normal signals, permission probes with signal 0, process-thread interactions, credential updates through `setuid()`, and `SIGURG` delivery through `F_SETOWN` on sockets.

## Important APIs, Types, and Functions

It uses `create_scoped_domain()`, kselftest fixtures, `sigaction()`, `kill()`, `raise()`, `pthread_create()`, `pthread_kill()`, `pthread_join()`, `setuid()`, UNIX stream sockets, `fcntl(F_SETOWN)`, `send(MSG_OOB)`, and pipe/fork synchronization. It reuses `scoped_base_variants.h` and common UNIX address helpers.

## Control Flow and State

Tests first prove a child can signal a parent before scoping and cannot afterward, then run the full parent/child domain topology matrix for `kill(pid, 0)`. Thread tests show same-process threads remain signalable regardless of whether scoping is applied before or after thread creation, and that libc `setuid()` still propagates credentials across threads. The `fown` fixture changes whether scoping happens before fork, before `F_SETOWN`, or after it, then checks whether OOB socket delivery can signal the child.

## Dependencies and Integration Points

It depends on Landlock signal scope enforcement, POSIX signal behavior, pthreads, capability handling for `setuid`, and UNIX socket ownership semantics.

## Risks and Test Signals

Risks include races around asynchronous signal delivery, treating same-thread-group signals as out-of-scope, breaking credential synchronization, and mishandling `F_SETOWN` when ownership predates scoping. Signals are `EPERM` on denied `kill`, unchanged `is_signaled` in parents, successful `pthread_kill`, successful thread credential checks, and variant-specific `SIGURG` receipt.
