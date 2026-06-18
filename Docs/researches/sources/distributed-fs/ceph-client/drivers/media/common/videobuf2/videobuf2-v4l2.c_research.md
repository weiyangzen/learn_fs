# sources/distributed-fs/ceph-client/drivers/media/common/videobuf2/videobuf2-v4l2.c

## Purpose
`videobuf2-v4l2.c` adapts the generic vb2 core to V4L2 userspace APIs. It validates and translates `struct v4l2_buffer`, sets V4L2 buffer flags/capabilities, handles media requests, exposes standard ioctl and file-operation helpers, and initializes `vb2_queue` instances for V4L2 drivers.

## Important APIs, Types, and Functions
Exports include `vb2_querybuf()`, `vb2_reqbufs()`, `vb2_create_bufs()`, `vb2_prepare_buf()`, `vb2_qbuf()`, `vb2_dqbuf()`, `vb2_streamon()`, `vb2_streamoff()`, `vb2_expbuf()`, `vb2_queue_init_name()`, `vb2_queue_init()`, `vb2_queue_release()`, `vb2_queue_change_type()`, `vb2_poll()`, standard `vb2_ioctl_*` helpers, standard `vb2_fop_*` helpers, `vb2_video_unregister_device()`, `vb2_request_validate()`, and `vb2_request_queue()`. Internal helpers include `__verify_planes_array()`, `__verify_length()`, `vb2_fill_vb2_v4l2_buffer()`, `set_buffer_cache_hints()`, `vb2_queue_or_prepare_buf()`, `__fill_v4l2_buffer()`, `__fill_vb2_buffer()`, and `vb2_find_buffer()`.

## Control Flow
Queue initialization checks V4L2 timestamp flags, sets `v4l2_buf_ops`, derives multiplanar/output/copy-timestamp flags from queue type, and calls the core initializer. `REQBUFS` and `CREATE_BUFS` validate memory/type, sanitize flags, populate capability bits, derive requested plane sizes from V4L2 formats, and delegate to core allocation. `PREPARE_BUF` and `QBUF` validate queue ownership, buffer index, type, memory, plane arrays, output lengths, cache hints, request FD semantics, and then call core prepare/qbuf. `DQBUF` delegates to the core, marks last capture-buffer state for `V4L2_BUF_FLAG_LAST`, and clears `DONE` before returning to userspace. Fill/copy functions translate vb2 plane state to/from single-planar and multiplanar V4L2 layouts, including timestamp, timecode, request FD, mapped/queued/done/error/prepared flags, and output-only flags. Ioctl and file-operation helpers add video-device ownership and locking around the core.

## State and Persistence
This layer stores V4L2-specific per-buffer metadata in `struct vb2_v4l2_buffer`: flags, field, timecode, sequence, request FD, held-buffer state, and plane copy data. Queue state includes timestamp policy, cache hint support, owner, file I/O ownership, request support, and last-buffer-dequeued tracking. State is volatile and tied to queue/device/file lifetimes.

## Dependencies and Integration Points
The file integrates with V4L2 core objects (`video_device`, `v4l2_fh`, events, ioctl ops, file ops), media requests, V4L2 buffer/format ABI definitions, and vb2 core. Drivers can either call the exported helpers directly from their ioctl implementations or install the standard `vb2_ioctl_*` and `vb2_fop_*` helpers.

## Risks and Edge Cases
Plane array length and output `bytesused`/`data_offset` validation protect against userspace overruns. `bytesused == 0` for output is deprecated but still optionally supported with `allow_zero_bytesused`. Request API use is mutually exclusive with direct QBUF and requires driver `buf_request_complete`; output request queues also need `buf_out_validate`. Cache hint flags are only honored for allowed MMAP queues. File I/O and streaming ioctls are mutually exclusive. Queue ownership helpers reject operations from other file handles once buffers are allocated or file I/O starts. `vb2_video_unregister_device()` takes a device reference so it can release queues after unregister without premature device free.

## Test Signals
Run `v4l2-compliance` across single-planar/multiplanar, capture/output, MMAP/USERPTR/DMABUF, request API, read/write, poll, expbuf, and remove-bufs cases. Useful runtime signals include correct capability bits, sanitized unknown flags, correct `EFAULT`/`EINVAL` for bad plane arrays and lengths, `EBUSY` for queue ownership conflicts, event polling through `EPOLLPRI`, and clean queue release on file close or video-device unregister.
