# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.h

## Purpose
Declares the videobuf2 queue wrappers, per-buffer state, grouped buffer-list abstraction, and queue-facing APIs used by IPU7 ISYS capture.

## Important APIs, Types, and Constants
`struct ipu7_isys_queue` embeds `struct vb2_queue`, a stream queue-node, device pointer, spinlock, incoming/active lists, and firmware output pin index. `struct ipu7_isys_buffer` is the list node plus an atomic error flag. `struct ipu7_isys_video_buffer` embeds `vb2_v4l2_buffer`, the ISYS buffer wrapper, and DMA address. Buffer-list flags `IPU_ISYS_BUFFER_LIST_FL_INCOMING`, `IPU_ISYS_BUFFER_LIST_FL_ACTIVE`, and `IPU_ISYS_BUFFER_LIST_FL_SET_STATE` control list requeue/completion behavior. Conversion macros map between vb2 queues, video objects, and buffer wrappers. Public functions expose list requeueing, firmware frame-buffer conversion, firmware-ready completion, and queue initialization.

## Control Flow and State
The header defines the state containers used by `ipu7-isys-queue.c`. Incoming buffers await synchronization across stream queues; active buffers have been submitted to firmware. A temporary `ipu7_isys_buffer_list` groups one buffer per active queue so the firmware command can describe all output pins for the same frame.

## Dependencies and Integration Points
Depends on Linux lists, spinlocks, atomics, `videobuf2-v4l2`, and forward declarations of firmware response/buffer set types. It is included by video and queue code, and its `fw_output` field is populated by firmware pin configuration in `ipu7-isys-video.c`.

## Risks and Test Signals
The data model assumes one DMA address per capture buffer and one active/incoming list membership at a time. Incorrect flag combinations can requeue buffers to the wrong list or complete them prematurely. Test signals are stable list lengths under stress, no WARNs from buffer-list count mismatches, correct error completion when `str2mmio_flag` is set, and valid `fw_output` indices for every configured output pin.
