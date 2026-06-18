# sources/distributed-fs/glusterfs/libglusterfs/src/event-poll.c

## Purpose
This file implements the portable `poll(2)` backend for GlusterFS's event subsystem. It is the fallback when epoll is unavailable and intentionally supports only one event thread.

## Important APIs, types, and functions
The backend exports `event_ops_poll` with `event_pool_new_poll`, register/select/unregister/close functions, `event_dispatch_poll`, no-op `event_reconfigure_threads_poll`, and `event_pool_destroy_poll`. Internal helpers include `__event_getindex`, `__flush_fd`, `event_dispatch_poll_resize`, and `event_dispatch_poll_handler`.

## Control flow
Pool creation allocates an event pool and registration array, creates a nonblocking breaker pipe, registers the read end, and forces `eventthreadcount` to 1. Registration appends an `event_slot_poll` entry and expands the array by 256 when full. Selection mutates event masks. Dispatch rebuilds the cached `pollfd` array when `changed` is set, polls with a 1 ms timeout, then invokes handlers for entries with `revents`.

## State and persistence behavior
The event pool holds a mutable registration array, cached `pollfd` array, breaker pipe fds, `used`, `count`, `changed`, and `activethreadcount`. State is in-memory only. Unregister removes entries by swapping the last used registration into the removed slot, so indexes can change.

## Dependencies and integration points
It depends on POSIX poll, pthreads, fcntl, GlusterFS memory/logging/syscall wrappers, and the common event API in `glusterfs/gf-event.h`. `event.c` falls back to this backend when epoll creation is unavailable or the platform lacks epoll.

## Risks and edge cases
Because unregister swaps entries, cached indexes can become stale and `__event_getindex()` must search by fd. The 1 ms timeout is simple but can wake frequently. Reallocation failure during registration can leave `event_pool->reg` NULL because `GF_REALLOC` result is assigned directly. Destroy frees the pool without destroying mutex/condition fields initialized elsewhere, unlike the epoll backend. The poll backend has no `event_handled` hook and no one-shot suppression, so handlers must tolerate level-triggered repeated readiness.

## Test signals
Tests should cover fallback creation, breaker pipe flushing, registration growth and realloc failure, stale index lookup, unregister swapping, select mask changes, dispatch resize after changes, handler invocation flags, destroy-mode loop exit, close-on-unregister, and behavior when multiple threads are requested.
