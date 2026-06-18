# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-queue.c

## Purpose
Implements videobuf2 queue operations and the runtime bridge from user capture buffers to IPU7 ISYS firmware frame-buffer commands. It coordinates multi-output streams by collecting one buffer from every capture queue before sending a firmware capture request.

## Important APIs, Types, and Functions
Exported functions are `ipu7_isys_buffer_list_queue()`, `ipu7_isys_buffer_to_fw_frame_buff()`, `ipu7_isys_queue_buf_ready()`, and `ipu7_isys_queue_init()`. The `vb2_ops` table provides `queue_setup`, `buf_init`, `buf_prepare`, `buf_cleanup`, `start_streaming`, `stop_streaming`, and `buf_queue`. Important internals include `buffer_list_get()`, `ipu7_isys_stream_start()`, `ipu7_isys_link_fmt_validate()`, `return_buffers()`, `get_sof_sequence_by_timestamp()`, and `ipu7_isys_buf_calc_sequence_time()`.

## Control Flow
Buffer initialization maps the scatterlist into IPU DMA/IOMMU space and stores the DMA address in the per-buffer wrapper. `buf_queue()` adds the buffer to the queue's incoming list; once media pipeline and all stream queues are ready, it attempts to pull a synchronized list. If the firmware stream is not yet running, it calls `ipu7_isys_stream_start()`, otherwise it converts the list into an `ipu7_insys_buffset`, moves buffers to active lists before firmware submission, and sends `IPU_INSYS_SEND_TYPE_STREAM_CAPTURE`. `start_streaming()` builds the media pipeline, validates link format, prepares stream metadata, waits until all queues in the stream are streaming, opens firmware, sets up hardware, and starts the initial capture. `stop_streaming()` stops firmware/subdevices, drops stream references, returns active/incoming buffers with error, and closes firmware.

## State and Persistence Behavior
Each `ipu7_isys_queue` owns spinlock-protected `incoming` and `active` lists. `struct ipu7_isys_buffer` tracks list membership and `str2mmio_flag`, while `struct ipu7_isys_video_buffer` persists mapped DMA address. `stream->buf_id` generates modulo-256 firmware frame IDs and `stream->sequence`/`seq[]` map SOF timestamps to V4L2 sequence numbers. State transitions are list-based and must remain consistent under spinlocks and `stream->mutex`.

## Dependencies and Integration Points
Depends on videobuf2 DMA-SG memory ops, IPU DMA mapping helpers, firmware ABI structs, firmware command submission, media pipelines, V4L2 subdev format helpers, TSC timestamp conversion, and `ipu7-isys-video.c` for stream open/close and setup. Firmware responses return through `ipu7_isys_queue_buf_ready()` via output pin callbacks configured by video stream setup.

## Risks and Test Signals
Critical risks are buffer leaks or double completion on stream-start failure, races between firmware buffer-ready responses and active-list insertion, missing cleanup when `ipu7_get_fw_msg_buf()` fails inside `ipu7_isys_stream_start()`, and timestamp fallback when TSC is zero or SOF history misses. Tests should cover single and multi-output streams, queued buffers before stream-on, insufficient synchronized buffers, stream-on failure unwinds, firmware timeout paths, DMA map/unmap balance, and matching returned firmware pin addresses to active buffers.
