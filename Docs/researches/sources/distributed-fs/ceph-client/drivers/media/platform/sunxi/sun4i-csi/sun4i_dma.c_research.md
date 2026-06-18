# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun4i-csi/sun4i_dma.c

Purpose: implements videobuf2 capture queue handling, DMA buffer programming, stream start/stop, and frame-done interrupt processing for sun4i CSI.

Important APIs and functions: public internal functions are `sun4i_csi_dma_register` and `sun4i_csi_dma_unregister`. Main vb2 callbacks are `sun4i_csi_queue_setup`, `sun4i_csi_buffer_prepare`, `sun4i_csi_buffer_queue`, `sun4i_csi_start_streaming`, and `sun4i_csi_stop_streaming`. IRQ entry is `sun4i_csi_irq`. Buffer helpers include scratch setup, slot fill, slot flip, and `return_all_buffers`.

Control flow: queue registration initializes locks, buffer list, vb2 queue, V4L2 device, and IRQ. Queued buffers are appended under `qlock`. Start streaming finds the configured CSI format, allocates a coherent scratch buffer large enough for all planes, starts the media pipeline, programs active width/height, polarities, input/output format, line length, two hardware buffer slots, double buffering, and frame-done interrupt, starts capture, then starts the source subdevice stream. On each frame interrupt, the status is acknowledged, the sequence number is assigned, the completed slot is returned to vb2, and the next queued or scratch buffer is programmed. Stop streaming stops the source and hardware, returns active/queued buffers as error, stops the pipeline, and frees the scratch buffer.

State and persistence: state is volatile in `csi->buf_list`, `current_buf[2]`, `scratch`, and `sequence`. DMA addresses are written directly to hardware registers and are valid only while buffers are queued and the device is powered. The scratch buffer prevents last-frame underruns when user buffers run out.

Dependencies and integration points: depends on videobuf2 V4L2 and DMA-contig helpers, media pipeline start/stop, V4L2 subdev `s_stream`, and register definitions from `sun4i_csi.h`. It relies on the V4L2 layer to populate `csi->fmt` and the core layer to register resources.

Risks: `q->min_queued_buffers = 3` with only two hardware slots relies on the scratch-buffer strategy and userspace queue depth. Error paths after `sun4i_csi_capture_start` must unwind hardware and pipeline consistently. No explicit overflow/line error interrupts are handled, only frame done. Format configuration writes active width as `width * 2`, which is format-specific and may not generalize if new formats are added.

Test signals: vb2 mmap and dmabuf streaming, queue underrun with scratch-buffer use, source subdev stream failure paths, IRQ-driven sequence increments, stop-streaming buffer states, and stress tests with rapid streamon/streamoff.
