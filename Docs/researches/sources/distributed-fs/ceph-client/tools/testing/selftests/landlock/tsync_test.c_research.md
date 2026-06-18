# sources/distributed-fs/ceph-client/tools/testing/selftests/landlock/tsync_test.c

## Purpose

`tsync_test.c` tests `LANDLOCK_RESTRICT_SELF_TSYNC`, which applies Landlock restrictions consistently across all threads in a process. It covers single-thread success, multi-thread synchronization, diverged thread domains, concurrent enablement, interruption/restart paths, and special no-ruleset flag combinations.

## Important APIs, Types, and Functions

The file creates a filesystem ruleset with `LANDLOCK_ACCESS_FS_WRITE_FILE | LANDLOCK_ACCESS_FS_TRUNCATE`, then uses `prctl(PR_SET_NO_NEW_PRIVS)`, `landlock_restrict_self(..., LANDLOCK_RESTRICT_SELF_TSYNC)`, pthread creation/cancel/join, cleanup handlers, `pthread_kill()`, `sigaction()`, and flag variants including logging flags.

## Control Flow and State

Idle threads sleep until canceled, storing their `no_new_privs` state through cleanup handlers. Tests enforce rulesets with TSYNC while sibling threads are live, intentionally diverge the main thread domain and resynchronize, and run two threads racing the same TSYNC call. The interruption test starts 200 idle threads plus a tight signaler thread to hit kernel cancellation/restart paths; userspace should still see success.

## Dependencies and Integration Points

It depends on Landlock TSYNC kernel support, pthreads, signal restart behavior, and kselftest metadata. It also exercises interactions with logging-related `landlock_restrict_self()` flags when `ruleset_fd == -1`.

## Risks and Test Signals

Risks include partial thread updates, missing implicit `no_new_privs`, deadlocks under signal interruption, or wrong errno for flag-only calls. Signals are all threads joining cleanly, cleanup handlers observing `no_new_privs`, both competing calls returning 0, interrupted TSYNC still succeeding, and expected `EBADF` or success for no-ruleset variants.
