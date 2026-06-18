# sources/distributed-fs/ceph-client/include/linux/watch_queue.h

## Purpose
`watch_queue.h` declares the user-mappable watch queue infrastructure used to deliver kernel object notifications through a pipe-backed queue. It supports filtering by notification type/subtype/info fields and attaching watches to watched objects.

## Important APIs, Types, and Functions
Under `CONFIG_WATCH_QUEUE`, `struct watch_type_filter` defines per-type subtype and info filters. `struct watch_filter` stores an RCU head or type bitmap plus a counted flexible array of filters. `struct watch_queue` stores an RCU filter pointer, backing pipe, watches list, preallocated notification pages, allocation bitmap, kref, lock, and sizing fields. `struct watch` links a watched object to a queue, stores owner creds, private data, ID, and kref. `struct watch_list` is embedded in watched objects and stores watcher hlist, release callback, and lock. APIs include `__post_watch_notification()`, `get_watch_queue()`, `put_watch_queue()`, `init_watch()`, `add_watch_to_object()`, `remove_watch_from_object()`, `watch_queue_set_size()`, `watch_queue_set_filter()`, `watch_queue_init()`, `watch_queue_clear()`, `init_watch_list()`, `post_watch_notification()`, `remove_watch_list()`, and `watch_sizeof()`. Without config support, `watch_queue_init()` returns `-ENOPKG`.

## Control Flow
A pipe is initialized as a watch queue, sized, and optionally filtered. Objects initialize a `watch_list`; clients create watches and attach them. When an object event occurs, `post_watch_notification()` calls the implementation, which checks filters and credentials, allocates a preallocated note slot, writes the notification into the pipe buffer, and wakes readers. Removing a watch or watch list unlinks under locks and frees by RCU/kref discipline.

## State and Persistence
State is runtime queue, filter, watch, and pipe-buffer state. Filters and watch lists are RCU-managed; watches and queues are refcounted. Notifications persist only until read from the pipe or queue teardown.

## Dependencies and Integration Points
Dependencies include uapi watch-queue notification formats, krefs, RCU, pipe internals, credentials, hlist, spinlocks, pages, and user-copy for filter setup. Integration points include key/keyring notifications and other watched kernel objects that embed `watch_list`.

## Risks
Lifetime management is subtle: filters, watches, watch lists, and queues use RCU plus krefs. Posting must handle closed pipes and exhausted note slots. Filter parsing must validate user-supplied sizes and type/subtype masks. Credential checks must prevent leaking notifications to unauthorized watchers. Config-disabled stubs must be handled by callers.

## Test Signals
Signals include watch queue pipe initialization, filter set/get behavior, notification delivery and reader wakeup, watch add/remove races, queue clear/close, RCU lifetime tests, invalid filter input, notification overflow handling, and builds without `CONFIG_WATCH_QUEUE`.
