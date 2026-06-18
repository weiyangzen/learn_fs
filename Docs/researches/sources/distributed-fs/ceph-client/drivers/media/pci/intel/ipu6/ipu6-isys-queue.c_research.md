# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu6/ipu6-isys-queue.c

## Purpose
`ipu6-isys-queue.c` implements the videobuf2 queue side of Intel IPU6 ISYS capture. It owns buffer allocation validation, DMA mapping, incoming/active buffer lists, multi-output buffer set assembly, streaming start/stop coordination, and completion of buffers when firmware reports pin data ready.

## Important APIs, Types, And Functions
The file implements `vb2_ops` through `ipu6_isys_queue_ops`: queue setup, buffer init/prepare/cleanup, start/stop streaming, and buffer queueing. Public helpers include `ipu6_isys_buffer_list_queue()`, `ipu6_isys_buf_to_fw_frame_buf()`, `ipu6_isys_queue_buf_ready()`, and `ipu6_isys_queue_init()`. It uses `struct ipu6_isys_queue` incoming/active lists, `struct ipu6_isys_buffer_list` as a per-frame multi-queue bundle, and `struct ipu6_isys_video_buffer` for the vb2 buffer plus IPU6 DMA address.

## Control Flow
`ipu6_isys_buf_init()` maps the first vb2 DMA-SG plane with `ipu6_dma_map_sgtable()` and caches the IOVA. `buf_queue()` appends the buffer to `aq->incoming`; once all queues in the shared firmware stream are streaming, it calls `buffer_list_get()` to remove one buffer from every queue, converts that list to `ipu6_fw_isys_frame_buff_set_abi`, moves buffers to active, and sends `STREAM_CAPTURE` to firmware.

`start_streaming()` walks the media graph from the video node to the CSI-2 subdev and external source, calls `ipu6_isys_setup_video()`, validates link format, opens firmware, prepares the stream for the first queue, and when every queue in the pipeline is ready sends `STREAM_START_AND_CAPTURE` through `ipu6_isys_stream_start()`. `stop_streaming()` stops firmware if this was the last queue, removes the queue from the stream, returns all remaining buffers as errors, and closes firmware.

## State And Persistence
All state is transient kernel memory. Incoming buffers are waiting for a complete multi-queue frame set; active buffers have been given to firmware. `stream->sequence` and the recent SOF timestamp ring are used to stamp completed buffers. If active buffers remain during cleanup, `isys->need_reset` is set so later opens fail until runtime power cycling clears the condition.

## Dependencies And Integration Points
This file integrates V4L2 vb2, media-controller pipelines, IPU6 firmware commands, IPU6 DMA mapping, CSI-2 SOF/EOF timestamping, and runtime firmware open/close in `ipu6-isys-video.c`. It expects `ipu6_isys_get_*()` format helpers and `ipu6_isys_setup_video()` to be valid for the video node.

## Risks And Test Signals
The highest-risk behavior is synchronization across multiple capture queues: a frame request is valid only when every queue has an incoming buffer. Error paths must avoid losing buffers if firmware stream open/start fails. `ipu6_isys_stream_start()` can return `-ENOMEM` after taking buffers if `ipu6_get_fw_msg_buf()` fails in its post-start loop, so stress with low memory and multiple queues matters. Tests should cover stream-on with missing buffers, multi-output capture, metadata capture, firmware timeouts, STR2MMIO errors, stream-off with active buffers, link-format mismatch, and repeated runtime PM cycles.
