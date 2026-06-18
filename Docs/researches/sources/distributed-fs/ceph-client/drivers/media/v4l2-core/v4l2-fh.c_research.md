# sources/distributed-fs/ceph-client/drivers/media/v4l2-core/v4l2-fh.c

## Purpose
`v4l2-fh.c` implements the standard V4L2 file-handle lifecycle. It initializes `struct v4l2_fh`, attaches it to a `struct file`, participates in per-video-device file-handle lists, owns per-open priority state, and provides close-time cleanup for media-source and event subscription state.

## Important APIs, Types, and Functions
The exported functions are `v4l2_fh_init`, `v4l2_fh_add`, `v4l2_fh_open`, `v4l2_fh_del`, `v4l2_fh_exit`, `v4l2_fh_release`, and `v4l2_fh_is_singular`. Important types are `struct v4l2_fh`, `struct video_device`, `struct file`, and the priority/event state accessed through `fh->prio`, `fh->wait`, `fh->available`, `fh->subscribed`, and `fh->subscribe_lock`.

## Control Flow
Drivers can either embed `struct v4l2_fh` or use `v4l2_fh_open`, which allocates one. `v4l2_fh_init` stores the video device pointer, inherits the video device control handler, initializes list heads and wait queues, sets the video-device `V4L2_FL_USES_V4L2_FH` flag, enables priority ioctls in `valid_ioctls`, initializes priority to unset, initializes event lists, sets sequence to `-1`, and initializes the subscription mutex.

`v4l2_fh_add` stores the file handle in `filp->private_data`, opens priority state through `v4l2_prio_open`, and adds the file handle to `vdev->fh_list` under `vdev->fh_lock`. `v4l2_fh_del` removes it from the list, closes priority state, and clears `private_data`. `v4l2_fh_exit` disables any media source associated with the video device, unsubscribes all events, destroys the subscription mutex, and nulls `fh->vdev`. `v4l2_fh_release` composes delete, exit, and free for handles allocated by `v4l2_fh_open`. `v4l2_fh_is_singular` checks whether this handle is the only entry in the video-device file-handle list.

## State and Persistence Behavior
State is per-open and in memory only. It persists for the lifetime of the open file and is exposed to other V4L2 helpers through `file_to_v4l2_fh`. Priority state affects ioctl arbitration. Event queues and subscriptions persist until explicit unsubscribe or close. `v4l2_fh_is_singular` is used by components such as flash helpers to determine first-open/last-close transitions.

## Dependencies and Integration Points
This file integrates with `v4l2-dev`, `v4l2-event`, `v4l2-ioctl`, V4L2 priority helpers, and media-controller source enabling/disabling through `v4l2-mc`. It is foundational for ioctl code that needs per-file priority, event dequeue, or control handlers.

## Risks
Drivers that mix embedded and allocated file handles must match the lifecycle correctly and not double-free. Missing `v4l2_fh_exit` leaks event subscriptions and leaves media sources enabled. The singular-open test is inherently moment-in-time and must be used under appropriate open/close serialization by callers. Clearing `private_data` affects all later helpers that assume `file_to_v4l2_fh` can return NULL.

## Test Signals
Test open/release paths, embedded-handle users, priority ioctl availability after init, event cleanup on release, media source disable on close, correct list membership under concurrent opens, and first-open/last-close consumers using `v4l2_fh_is_singular`.
