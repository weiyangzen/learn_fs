# sources/distributed-fs/ceph-client/fs/notify/group.c

## Purpose

`group.c` owns allocation, reference counting, shutdown, and final destruction of `struct fsnotify_group`. A group is the per-user/per-backend notification endpoint that owns marks, queued events, wait queues, backend-private data, and backend operations.

## Important APIs, Types, and Functions

Important functions are `fsnotify_alloc_group()`, `fsnotify_get_group()`, `fsnotify_put_group()`, `fsnotify_group_stop_queueing()`, `fsnotify_destroy_group()`, and `fsnotify_fasync()`. Internal helpers are `__fsnotify_alloc_group()` and `fsnotify_final_destroy_group()`.

## Control Flow

Group allocation zeroes and initializes the group, sets refcount and `user_waits`, initializes notification and mark locks/lists, assigns ops/flags, and defaults `max_events` to `UINT_MAX`. Destruction first stops queueing, clears all marks by group, waits for marks pinned by userspace permission waits, waits for asynchronous mark destruction, flushes queued notifications, frees the per-group overflow event, then drops the final reference. Final destroy invokes backend `free_group_priv`, drops memcg, destroys `mark_mutex`, and frees the group.

## State and Persistence Behavior

Group state persists for the lifetime of a fanotify/inotify file descriptor or other backend endpoint. `shutdown` prevents future queue insertion. `notification_list`, `marks_list`, `overflow_event`, fasync state, memcg, and backend-private fields are owned through the group. Refcounting allows marks and external users to keep the group alive until asynchronous cleanup finishes.

## Dependencies and Integration Points

It depends on generic fsnotify backend definitions, mark cleanup in `mark.c`, notification queue cleanup in `notification.c`, memcg references, wait queues, fasync, and backend ops supplied by fanotify/inotify/dnotify-style users.

## Risks and Edge Cases

The risky sequence is teardown while permission events or mark destruction are in progress. The group must stop queueing early, wait for `user_waits`, and wait for mark SRCU reapers before flushing notifications so no handler can still enqueue or reference the group. Overflow events are special and cannot be freed by generic event destruction.

## Test Signals

Tests should close fanotify/inotify descriptors with queued normal events, overflow events, pending permission events, and active marks. Race tests should remove marks while closing groups and verify no leaks, use-after-free, or stuck waiters. Fasync behavior is covered by SIGIO readiness tests for inotify users.
