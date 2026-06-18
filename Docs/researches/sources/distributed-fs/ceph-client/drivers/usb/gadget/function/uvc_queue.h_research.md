# sources/distributed-fs/ceph-client/drivers/usb/gadget/function/uvc_queue.h

## Purpose

`uvc_queue.h` declares the UVC gadget video queue abstraction shared by V4L2 and USB streaming code. It wraps videobuf2 objects with UVC-specific state needed for request encoding and completion.

## Important APIs, Types, and Functions

The header defines `UVC_MAX_FRAME_SIZE`, `UVC_MAX_VIDEO_BUFFERS`, `enum uvc_buffer_state`, `struct uvc_buffer`, and `struct uvc_video_queue`. Public operations mirror the implementation in `uvc_queue.c`: initialization, buffer allocation/query/queue/dequeue, poll, mmap, cancellation, stream enable/disable, completion, and head lookup. `uvc_queue_streaming()` is an inline `vb2_is_streaming()` wrapper.

## Control Flow

V4L2 code calls allocation and queue/dequeue helpers from ioctl paths. USB video code calls `uvcg_queue_head()` while filling USB requests and `uvcg_complete_buffer()` when the final request for a buffer completes. Stream transitions pass through `uvcg_queue_enable()`, while disconnect/error paths call `uvcg_queue_cancel()`.

## State and Persistence Behavior

`UVC_QUEUE_DISCONNECTED` gates new queued buffers after disconnect. `UVC_QUEUE_DROP_INCOMPLETE` marks the next completed buffer as an error after transfer loss. `sequence` and `buf_used` are per-stream counters. The IRQ list is transient and protected by `irqlock`.

## Dependencies and Integration Points

The header depends on list, poll, spinlock, and `videobuf2-v4l2` APIs. It is included by UVC V4L2 and video-transfer implementation files and forms their shared buffer contract.

## Risks and Test Signals

Risks include callers touching `irqqueue` without holding `irqlock`, incorrect state transitions between queued/active/done/error, and forgetting that SG cursor fields are meaningful only when `use_sg` is set. Test signals are compile coverage, streamon/streamoff transitions, disconnect cancellation, and both SG and non-SG streaming.
