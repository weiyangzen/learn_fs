# sources/distributed-fs/ceph-client/include/media/v4l2-event.h

Purpose: declares the V4L2 event framework for per-filehandle subscriptions, queued kernel events, event dequeue, event wakeups, and helper subscription filters for source-change and subdevice events.

Important APIs/types: `struct v4l2_kevent` wraps a userspace `v4l2_event`, timestamp, list node, and parent subscription. `struct v4l2_subscribed_event_ops` allows event classes to run add/delete hooks and replace or merge queued events. `struct v4l2_subscribed_event` records type/id/flags, owning `v4l2_fh`, object linkage, ring-buffer indices (`elems`, `first`, `in_use`), and a flexible array of queued events.

Control flow: a driver or helper subscribes with `v4l2_event_subscribe()` or a specialized helper, queues events globally with `v4l2_event_queue()` or to one file handle with `v4l2_event_queue_fh()`, userspace dequeues through `v4l2_event_dequeue()`, and unregister paths wake blocked file handles with `v4l2_event_wake_all()`. Unsubscribe paths remove one or all subscriptions and call delete hooks.

State and persistence: event state lives in each `v4l2_fh`: subscribed list, available list, wait queue, `navailable`, and sequence counter. Subscription ring buffers may replace or merge events to cap queue length. There is no durable persistence beyond open file lifetime.

Dependencies and integration: includes videodev2 and wait queues, and forward-depends on `v4l2_fh`, `video_device`, and `v4l2_subdev`. Control events integrate with `v4l2-ctrls.h` through `v4l2_ctrl_sub_ev_ops`; source-change helpers integrate with decoder/input drivers and subdevice core ops.

Risks: incorrect `elems` sizing causes lost events; add/delete callbacks must be serialized by the filehandle subscription lock; event data fields are driver-owned while sequence/timestamp/pending are core-owned; and unregister must wake waiters to avoid blocked readers.

Test signals: subscribe/unsubscribe one and all events, queue to all file handles and one file handle, dequeue blocking and nonblocking, verify sequence/pending values, exercise replace/merge callbacks with a one-entry queue, source-change filters, and subdevice unsubscribe helper behavior.
