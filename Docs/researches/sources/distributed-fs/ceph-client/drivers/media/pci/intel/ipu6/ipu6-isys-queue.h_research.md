# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.h

## Purpose
This header defines the queue and buffer objects used by IPU6 ISYS video nodes and declares the queue/firmware conversion entry points implemented in `ipu6-isys-queue.c`.

## Important APIs, Types, And Data
`struct ipu6_isys_queue` wraps a `vb2_queue`, a media-stream list node, spinlock-protected `active` and `incoming` buffer lists, and the firmware output pin index. `struct ipu6_isys_buffer` is the list node embedded in capture buffers plus an atomic STR2MMIO error flag. `struct ipu6_isys_video_buffer` embeds `vb2_v4l2_buffer`, the ISYS buffer node, and the mapped DMA address. `struct ipu6_isys_buffer_list` is a temporary list of one buffer from each queue. The two flags, `IPU6_ISYS_BUFFER_LIST_FL_INCOMING` and `_ACTIVE`, select where a bundle is returned.

The declared APIs are `ipu6_isys_buffer_list_queue()`, `ipu6_isys_buf_to_fw_frame_buf()`, `ipu6_isys_queue_buf_ready()`, and `ipu6_isys_queue_init()`.

## Control Flow
The header supports a two-list queueing model. User buffers enter `incoming`, are bundled across all queues in a stream, then move to `active` just before firmware receives the frame-buffer-set command. Firmware completion later removes the matching active buffer and completes the vb2 buffer.

## State And Persistence
The structures store only live queue state for the current device lifetime. DMA addresses are set during vb2 buffer initialization and cleared on cleanup. No persistent storage is used.

## Dependencies And Integration Points
The header depends on vb2 V4L2 types and IPU6 firmware ABI structures. It is included by video and queue code and forward-declares `struct ipu6_isys_stream` to avoid a deeper include cycle.

## Risks And Test Signals
The conversion macros assume the exact embedding layout of queue and buffer structures. Tests should exercise all vb2 paths that use these macros: queue setup, buffer prepare, stream start/stop, capture completion, and error completion.
