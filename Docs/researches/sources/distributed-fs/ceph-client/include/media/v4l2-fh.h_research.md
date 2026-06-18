# sources/distributed-fs/ceph-client/include/media/v4l2-fh.h

Purpose: declares the mandatory V4L2 per-open filehandle object that connects a `struct file` to a `video_device`, control handler, priority state, event queues, and optional mem2mem context.

Important APIs/types: `struct v4l2_fh` stores list linkage into `video_device->fh_list`, `vdev`, per-file `ctrl_handler`, priority, event wait queue, subscription mutex, subscribed and available event lists, available count, event sequence, and `m2m_ctx`. `file_to_v4l2_fh()` returns `file->private_data` as a `v4l2_fh`.

Control flow: drivers call `v4l2_fh_init()` in open, then `v4l2_fh_add()` to link the handle and set `file->private_data`. Simple drivers can use `v4l2_fh_open()` as the open operation. Release paths call `v4l2_fh_del()` to unlink/reset private data, then `v4l2_fh_exit()` to release framework resources; `v4l2_fh_release()` bundles delete/exit/free for simple drivers. `v4l2_fh_is_singular()` checks whether this is the only open handle for exclusive operations.

State and persistence: all state is per open file and is torn down on release. Event subscriptions and queued events are stored here; the optional mem2mem context links queue/scheduler state to this open. `v4l2_fh_init()` also sets the `V4L2_FL_USES_V4L2_FH` flag on the video device per the device header contract.

Dependencies and integration: includes fs, list, kconfig, and videodev2. It integrates with `v4l2-dev.h` file-handle lists, `v4l2-event.h` queues, `v4l2-ctrls.h` per-file control handlers, priority helpers, and `v4l2-mem2mem.h` contexts.

Risks: bypassing `v4l2_fh_add()` leaves `file->private_data` unset; failing to call `v4l2_fh_exit()` leaks event subscriptions; accessing `file->private_data` directly can hide non-V4L2 private layouts; singular checks are only meaningful while the fh list is correctly maintained.

Test signals: open/release using helper and custom paths, private-data reset on delete, event subscription cleanup on exit, singular detection with one and multiple opens, priority propagation, and mem2mem context association.
