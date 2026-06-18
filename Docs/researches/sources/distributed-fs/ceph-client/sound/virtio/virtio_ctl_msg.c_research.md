<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c -->
# sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c

## Purpose
Virtio-snd synchronous/asynchronous control-message transport over the control virtqueue, including allocation, lifetime management, completion, cancellation, and configuration queries.

## APIs, Types, and Functions
Defines private `struct virtio_snd_msg`. Exports `virtsnd_ctl_msg_ref()`, `virtsnd_ctl_msg_unref()`, request/response accessors, `virtsnd_ctl_msg_alloc()`, `virtsnd_ctl_msg_send()`, `virtsnd_ctl_msg_complete()`, `virtsnd_ctl_msg_cancel_all()`, `virtsnd_ctl_query_info()`, and `virtsnd_ctl_notify_cb()`.

## Control Flow, State, and Persistence
Allocation stores request and response payloads after the message header and initializes scatterlists, completion, list node, and refcount. Send sets default response to IO error, assembles up to four sg entries, adds the message to the control virtqueue under queue lock, records it in `snd->ctl_msgs`, notifies the device, and optionally waits for completion with `virtsnd_msg_timeout_ms`. Completion removes the list entry, completes waiters, and drops the queue-owned reference. Cancellation drains pending messages and completes them with the default error. Query-info sends a standard `virtio_snd_query_info` request with an inbound data sg.

## Dependencies and Integration
Depends on virtqueue scatter-gather APIs, completions, refcounting, module parameter timeout from `virtio_card.c`, and all parsers/control callbacks that issue virtio requests.

## Risks and Test Signals
Risks include timeout races where late device completion may touch still-pending messages, default cancellation status semantics, nowait lifetime expectations, and interrupt callback lock ordering. Test signals are query-info paths, concurrent controls, timeout/cancel injection, remove with pending messages, and response status mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/virtio/virtio_ctl_msg.c -->
