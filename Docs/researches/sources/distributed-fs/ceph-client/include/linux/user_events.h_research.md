# sources/distributed-fs/ceph-client/include/linux/user_events.h

## Purpose
This header defines kernel bookkeeping for user_events tracing registrations attached to an `mm_struct` and task lifecycle hooks.

## Important APIs, types, and functions
With `CONFIG_USER_EVENTS`, key type `user_event_mm` tracks mm list links, enablers, refcounts for mm/tasks, and deferred RCU cleanup. APIs are `user_event_mm_dup()`, `user_event_mm_remove()`, and inline hooks `user_events_fork()`, `user_events_execve()`, and `user_events_exit()`. Disabled builds provide no-op hooks.

## Control flow, state, and persistence
On fork, tasks sharing the VM increment task refs; non-`CLONE_VM` forks duplicate user_event mm state. Exec and exit remove task/mm associations. State is runtime tracing enablement tied to process address spaces and protected by tracing internals; no persistent state is stored.

## Dependencies and integration points
It depends on list, refcount, mm types, RCU work, and the user_events UAPI. It integrates with task fork/exec/exit paths and tracing/eventfs user-event registration.

## Risks and test signals
Risks include refcount leaks, use-after-free across fork/exec/exit, and incorrect handling of shared VM tasks. Tests should exercise clone with and without `CLONE_VM`, exec cleanup, exit cleanup, and disabled-config stubs.
