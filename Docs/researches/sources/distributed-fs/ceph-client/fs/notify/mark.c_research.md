# sources/distributed-fs/ceph-client/fs/notify/mark.c

## Purpose

`mark.c` implements fsnotify mark and connector lifetime, locking, reference counting, mask recalculation, object attachment, group attachment, lookup, clearing, unmount scanning, and asynchronous destruction. It is the concurrency core that makes inode/mount/superblock/mount-namespace watch lists safe for lockless SRCU event delivery.

## Important APIs, Types, and Functions

Key exported functions include `fsnotify_get_mark()`, `fsnotify_put_mark()`, `fsnotify_prepare_user_wait()`, `fsnotify_finish_user_wait()`, `fsnotify_detach_mark()`, `fsnotify_free_mark()`, `fsnotify_destroy_mark()`, `fsnotify_compare_groups()`, `fsnotify_unmount_inodes()`, `fsnotify_add_mark_locked()`, `fsnotify_add_mark()`, `fsnotify_find_mark()`, `fsnotify_clear_marks_by_group()`, `fsnotify_destroy_marks()`, `fsnotify_init_mark()`, `fsnotify_wait_marks_destroyed()`, and `fsnotify_init_connector_caches()`. Internal helpers manage connector allocation, sb info attachment, watched-object counters, inode references, mask recalculation, connector detachment, and reaper work.

## Control Flow

Adding a mark initializes group state, inserts the mark on the group's list under `group->mark_mutex`, attaches or creates an object connector, inserts the mark into the connector list sorted by group priority/address, updates superblock watched-object counters, sets the connector pointer, and recalculates object masks. Event delivery walks connector lists under `fsnotify_mark_srcu`; permission waits can pin marks with `fsnotify_prepare_user_wait()`, drop SRCU while waiting for userspace, then reacquire SRCU and put marks. Destroy paths detach a mark from the group list, drop the list reference, eventually remove it from the connector list on final put, detach empty connectors from objects, drop inode refs outside spinlocks, queue connectors and marks for SRCU-delayed free, and run delayed work reapers.

## State and Persistence Behavior

Persistent state includes object connector pointers in inodes, mounts, superblocks, and mount namespaces; connector mark lists; object aggregate masks; sb `fsnotify_sb_info` watched-object counters and inode connector list; mark flags/masks/refcounts; and global destroy queues. Inode connectors may hold inode references unless all attached marks are evictable. Superblock deletion waits for watched-object counters to fall to zero. Destroyed marks remain allocated until both refcount and SRCU grace period permit final backend free.

## Dependencies and Integration Points

It depends on fsnotify backend structures, VFS inode/mount/sb/mntns fields, SRCU, workqueues, slab caches, refcounts, spinlocks/mutexes, and atomic counters. Backends call it to create/destroy marks; `fsnotify.c` reads connector lists and aggregate masks; fdinfo walks group marks; superblock teardown calls unmount cleanup.

## Risks and Edge Cases

The lock order is strict: `group->mark_mutex`, then `mark->lock`, then `connector->lock`. Violating it risks deadlock. Connector detachment must handle concurrent group clear, object clear, event delivery, and evictable inode marks. A concurrent attach/detach can delay clearing inode refs to avoid losing required pins. Group priority sorting is required for fanotify classes and ignore-mask correctness. `fsnotify_clear_marks_by_group()` cannot safely free arbitrary list entries after dropping the mutex, so it repeatedly frees the first selected mark.

## Test Signals

Signals include lockdep coverage, KASAN/KCSAN race testing, fanotify/inotify mark add/remove/flush stress, unmount with watched inodes, inode eviction with evictable and non-evictable marks, permission waits during close, priority ordering across notification classes, and watched-object counter assertions during superblock deletion.
