# sources/distributed-fs/ceph/src/rgw/driver/posix/notify.h

## Purpose
`notify.h` defines the notification abstraction used by the POSIX bucket listing cache and implements the Linux inotify backend inline. It converts filesystem create/delete/move and overflow signals into bucket-cache events.

## Important APIs, Types, and Functions
`Notifiable` declares `EventType::{ADD, REMOVE, INVALIDATE}`, `Event`, and virtual `notify(bucket_name, opaque, events)`. `Notify` stores the callback object and bucket root path, and declares `factory()`, `add_watch()`, and `remove_watch()`.

`Inotify` owns the Linux implementation. It has watch and event fds, a mutex-protected descriptor-to-`WatchRecord` map and name-to-descriptor map, an atomic shutdown flag, and a background thread. `add_watch()` calls `inotify_add_watch()` on `bucket_root / dname`; `remove_watch()` calls `inotify_rm_watch()` and erases both maps. `ev_loop()` polls the inotify fd and eventfd, reads batches into an aligned buffer, maps each watch descriptor to a bucket name/opaque pointer, and calls `Notifiable::notify()`.

## Control Flow
The constructor initializes inotify/eventfd and starts `ev_loop()`. The loop waits in `poll()`, reads inotify events, skips stale watch descriptors, translates create and moved-to events into ADD, delete and moved-from into REMOVE, and queue overflow into INVALIDATE. Each translated batch is sent to the registered `Notifiable`.

The destructor sets shutdown, writes to eventfd to wake the poll, joins the thread, and closes fds. `BucketCache` resets the notifier before draining entries so callbacks do not race with cache destruction.

## State and Persistence Behavior
All state is in memory and kernel watch state. There is no durable persistence. Watch records store the logical bucket name and an opaque cache-entry pointer so callbacks can reject stale events after recycling.

## Dependencies and Integration Points
The file depends on Linux inotify/eventfd/poll APIs, `unordered_dense.h`, `fmt`, threads, mutexes, atomics, and filesystem paths. It integrates with `BucketCache::fill()` to add watches and `BucketCacheEntry::reclaim()` to remove watches.

## Risks
The eventfd is only used as a wakeup fd; `ev_loop()` does not read/drain it, which is acceptable for shutdown but would matter for repeated signals. `aw_mask` excludes many event types and ignores modifications, so metadata-only or write-only changes may not update cached listings. Duplicate `add_watch()` uses unordered-dense `insert()` and will not update an existing mapping. `event->name` is a string view into the read buffer and is safe only during immediate notification processing. Constructor starts the thread after member initialization, but failures call `exit(1)`.

## Test Signals
Tests should create/remove/move files in watched bucket directories and assert ADD/REMOVE delivery, force overflow or direct INVALIDATE handling, add/remove watches repeatedly, test duplicate watches, run under thread sanitizer for destructor races, and verify stale descriptor events are ignored.
