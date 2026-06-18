<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h

Purpose: defines notification pipe watch queue records, filters, removal records, and key/keyring notification payloads.

Important APIs and types: `O_NOTIFICATION_PIPE` selects notification pipes via `pipe2()`. Ioctls set queue size and filters. `struct watch_notification` encodes type, subtype, length, watch ID, and type-specific info flags. Filter structures match notification types, info masks, and subtype bitmaps. Meta notifications report removal and loss. `struct key_notification` reports key instantiation, update, link/unlink, clear, revoke, invalidate, and setattr events.

Control flow, state, and persistence: userspace creates a notification pipe, sets size/filter, attaches watches through subsystem APIs, and reads records. Queue contents are transient; watched object state lives in the producing subsystem.

Dependencies and integration points: integrates pipes, keyrings, file notification-style watchers, and ioctl control.

Risks and test signals: risks include bitfield ABI layout, record length validation, filter masking, loss notification, and flexible-array bounds. Test queue sizing, filter rules, keyring events, watch removal, overflow/loss, and 32/64-bit readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/watch_queue.h -->
