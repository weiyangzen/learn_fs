# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-event.c

## Purpose
`v4l2-event.c` implements V4L2 event subscription, queueing, dequeueing, wakeup, and unsubscribe behavior for `struct v4l2_fh` file handles. It gives drivers a shared event queue model with per-subscription ring buffers, sequence numbers, timestamps, and type-specific merge/replace hooks.

## Important APIs, Types, and Functions
Exported APIs include `v4l2_event_dequeue`, `v4l2_event_queue`, `v4l2_event_queue_fh`, `v4l2_event_pending`, `v4l2_event_wake_all`, `v4l2_event_subscribe`, `v4l2_event_unsubscribe_all`, `v4l2_event_unsubscribe`, `v4l2_event_subdev_unsubscribe`, `v4l2_src_change_event_subscribe`, and `v4l2_src_change_event_subdev_subscribe`. Core types are `struct v4l2_fh`, `struct v4l2_subscribed_event`, `struct v4l2_kevent`, `struct v4l2_event`, and `struct v4l2_subscribed_event_ops`.

## Control Flow
`v4l2_event_subscribe` rejects `V4L2_EVENT_ALL`, normalizes queue depth to at least one, allocates a flexible `v4l2_subscribed_event`, initializes embedded event slots, and adds it to `fh->subscribed` under `fh->vdev->fh_lock` while serialized by `fh->subscribe_lock`. Duplicate subscriptions are treated as success after freeing the new allocation. Optional `ops->add` can initialize driver-specific subscription state; failure removes and frees the subscription.

Queueing starts at `v4l2_event_queue` for all file handles on a video device, or `v4l2_event_queue_fh` for one handle. Both take `fh_lock` and call `__v4l2_event_queue_fh`, which first checks whether the file handle subscribed to the event type/id. If the subscription ring is full, the oldest queued event is removed and either replaced or merged through subscription ops. The new event is filled with type, id, payload, timestamp, and incremented per-file-handle sequence number, added to `fh->available`, and waiters are woken.

`v4l2_event_dequeue` supports nonblocking dequeue directly and blocking dequeue through `wait_event_interruptible`, temporarily releasing `vdev->lock` while sleeping. Dequeue removes the oldest available event, updates pending count and timestamp, advances the subscription ring head, and decrements in-use count. Unsubscribe removes pending events from `fh->available`, calls optional `ops->del`, removes the subscription list node, and frees it. Source-change subscriptions use merge/replace hooks that OR change bits.

## State and Persistence Behavior
All event state is per open file handle and in memory only. `fh->available`, `fh->navailable`, `fh->sequence`, and each subscription's `first`, `in_use`, and event array define queue state. Timestamps are captured using `ktime_get_ns` when queued and converted to `timespec64` when dequeued. Closing a file handle via `v4l2_fh_exit` is expected to call `v4l2_event_unsubscribe_all`.

## Dependencies and Integration Points
The file depends on `v4l2-fh` initialization, `video_device` file-handle lists and locks, wait queues, spinlocks, mutexes, and V4L2 ioctl wrappers for `VIDIOC_DQEVENT`, `VIDIOC_SUBSCRIBE_EVENT`, and `VIDIOC_UNSUBSCRIBE_EVENT`. Subdevice event wrappers use the same core logic.

## Risks
Correct lock ordering is critical: subscription changes use `subscribe_lock` plus `fh_lock`, while queue/dequeue use `fh_lock` and dequeue may release/reacquire `vdev->lock`. Ring full behavior must maintain `fh->navailable` and list membership exactly or pending counts go stale. Merge/replace hooks can change payload semantics, so event types with lossy queues need tests. Blocking dequeue must handle wakeups where no event remains, retrying on `-ENOENT`.

## Test Signals
Test duplicate subscribe, queue depth one replacement, queue depth greater than one merge, blocking and nonblocking dequeue, pending counts, unsubscribe with pending events, unsubscribe-all during close, source-change bit merging, multiple file handles subscribed to the same event, and lockdep under concurrent queue/dequeue/unsubscribe.
