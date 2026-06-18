# sources/distributed-fs/ceph-client/drivers/media/platform/atmel/atmel-isi.c

## Purpose
This driver exposes the Atmel Image Sensor Interface as a V4L2 capture device connected to one async-bound camera subdevice over an OF graph endpoint. It configures ISI geometry, bus polarity, DMA descriptors, and format conversion/swap settings, then streams sensor frames into vb2 DMA-contiguous buffers.

## Important APIs, Types, and Functions
`struct atmel_isi` contains register base, clock, IRQ, runtime PM state, V4L2/vb2 objects, async notifier, current format, supported user formats, DMA descriptor pool, queued buffers, and the active buffer. `struct fbd`, `struct isi_dma_desc`, and `struct frame_buffer` model hardware frame descriptors and vb2 buffers. Key functions include `configure_geometry()`, `isi_interrupt()`, `atmel_isi_wait_status()`, `start_dma()`, `start_streaming()`, `stop_streaming()`, `isi_try_fmt()`, `isi_set_fmt()`, `isi_formats_init()`, `isi_graph_init()`, and `atmel_isi_probe()`.

## Control Flow
Probe parses the endpoint, registers a V4L2 device, allocates the video node and vb2 queue, allocates a coherent descriptor array, maps registers, requests IRQ, initializes an async notifier, and enables runtime PM. When the remote subdevice binds and the notifier completes, the driver discovers overlapping media-bus formats, programs bus parameters, sets a default VGA format, and registers the video device. On open, the sensor is powered and the active format is pushed to the subdevice. `STREAMON` resumes runtime PM, starts the sensor stream, resets ISI, disables stale IRQs, programs geometry, and starts DMA for the active queued buffer. Transfer-complete IRQs complete the active buffer and arm the next descriptor. `STREAMOFF` stops the sensor, returns queued buffers as errors, waits for codec-path completion if needed, disables interrupts/ISI, and releases runtime PM.

## State and Persistence
Runtime state is in `atmel_isi`, the DMA descriptor free list, `video_buffer_list`, `active`, `fmt`, `current_fmt`, and `sequence`. Nothing persists across unbind. `lock` serializes file/vb2 operations, while `irqlock` protects active/queued buffer state shared with the ISR. Runtime PM gates the peripheral clock.

## Dependencies and Integration Points
The driver uses V4L2 device/video/subdev APIs, V4L2 async notifier, V4L2 fwnode endpoint parsing, OF graph, vb2 DMA-contig, runtime PM, and one `isi_clk` clock. It calls subdevice `s_power`, `s_stream`, `set_fmt`, `enum_mbus_code`, `enum_frame_size`, and frame interval operations. Register constants and platform data are defined in `atmel-isi.h`.

## Risks and Edge Cases
Reset and disable completion require a camera pixel clock; missing sensor clocking can cause 500 ms timeouts. Descriptor count is capped at `VIDEO_MAX_FRAME`; buffers fail prepare if descriptors are exhausted. Preview versus codec DMA path is selected from the output fourcc, so unsupported format combinations can route to the wrong channel if format tables drift. `clamp(..., 0U, MAX)` permits zero width/height through the clamp before subdevice negotiation. Sensor subdevice failures during stream-on must return queued buffers to vb2.

## Test Signals
Test OF endpoints for 8-bit, 10-bit, BT.656 embedded sync, and sync/pixel-clock polarities. Validate supported format discovery against multiple sensors, `VIDIOC_ENUM_FMT`, `TRY/S_FMT`, frame size/interval forwarding, MMAP/READ/DMABUF streaming, reset/disable timeout logs, runtime suspend/resume clock gating, and buffer return state on stream-on failure and stream-off.
