# sources/distributed-fs/ceph-client/include/media/videobuf2-v4l2.h

Purpose: This header adapts the vb2 core queue framework to the V4L2 userspace ABI. It defines the V4L2-specific buffer wrapper and public helpers used by V4L2 ioctl and file-operation implementations.

Important APIs, types, and functions: `struct vb2_v4l2_buffer` embeds `struct vb2_buffer` and adds V4L2 flags, field order, timecode, sequence, request fd, hold-capture flag, and V4L2 plane array. `to_vb2_v4l2_buffer()` casts from core buffer to V4L2 buffer. Queue wrappers include `vb2_find_buffer()`, `vb2_querybuf()`, `vb2_reqbufs()`, `vb2_create_bufs()`, `vb2_prepare_buf()`, `vb2_qbuf()`, `vb2_expbuf()`, `vb2_dqbuf()`, `vb2_streamon()`, `vb2_streamoff()`, `vb2_queue_init()`, `vb2_queue_init_name()`, `vb2_queue_release()`, `vb2_queue_change_type()`, and `vb2_poll()`. Ioctl helpers implement request/create/query/prepare/qbuf/dqbuf/stream/export/remove operations. File-operation helpers implement mmap, release, read, write, poll, and no-MMU get-unmapped-area. Request API helpers are `vb2_request_validate()` and `vb2_request_queue()`.

Control flow: V4L2 drivers wire these helpers into `v4l2_ioctl_ops` and `v4l2_file_operations`. The wrapper validates V4L2 buffer type and memory fields, maps request fds to media requests when available, calls vb2 core, and fills or consumes `struct v4l2_buffer` fields. Helper ioctl paths also serialize on `vb2_queue->lock` or `video_device->lock` and enforce queue ownership through `vb2_queue_is_busy()`.

State and persistence behavior: State extends vb2 core queue state with V4L2 metadata per buffer and optional subsystem flags such as mem2mem hold-capture support. Queue ownership in `q->owner` prevents unrelated file handles from manipulating the same queue.

Dependencies and integration points: It depends on `linux/videodev2.h`, `videobuf2-core.h`, `struct video_device`, `struct media_device`, V4L2 file handles, and media request support. It integrates directly with the V4L2 ioctl ABI, poll/read/write/mmap file operations, video-device unregister, and request API validation.

Risks: ABI translation must keep `VIDEO_MAX_FRAME/PLANES` aligned with vb2 constants, enforced by preprocessor checks. Request fd binding must not mix direct QBUF and request queueing. Queue ownership checks are critical for multi-open devices. `vb2_video_unregister_device()` should be used when release helpers are used, or stream shutdown ordering can be wrong during unbind.

Test signals: Run V4L2 compliance for query/req/create/prepare/qbuf/dqbuf/expbuf/streamon/streamoff, multi-open ownership cases, request API queuing, mem2mem hold-capture behavior, poll events, file read/write emulation, mmap/no-MMU paths, queue type changes before allocation, and unregistration with streaming active.
