# sources/distributed-fs/ceph-client/drivers/media/platform/nxp/imx7-media-csi.c

## Purpose
`imx7-media-csi.c` implements the i.MX6UL/i.MX7/i.MX8MQ CSI capture bridge as a V4L2 subdevice plus a video capture node. It receives pixels from a parallel source, a CSI-2 receiver, or a muxed upstream entity, configures the CSI hardware, and writes frames into videobuf2 DMA-contiguous capture buffers.

## Important APIs, Types, and Functions
`struct imx7_csi` is the central state object. It stores MMIO, IRQ, clock, media and V4L2 devices, async notifier, source subdevice, CSI-2 detection, CSI subdev pads, video device, capture format, compose rectangle, vb2 queue, ready queue, two active hardware framebuffer slots, a coherent underrun buffer, streaming state, frame sequence, EOF completion state, and model data. `struct imx7_csi_pixfmt` maps memory FourCCs to media bus codes, bits per pixel, and YUV/RGB classification.

Hardware helpers include `imx7_csi_reg_read()`, `imx7_csi_reg_write()`, `imx7_csi_irq_clear()`, `imx7_csi_init_default()`, `imx7_csi_configure()`, `imx7_csi_enable()`, `imx7_csi_disable()`, and `imx7_csi_error_recovery()`. DMA and buffer helpers include `imx7_csi_alloc_dma_buf()`, `imx7_csi_dma_setup()`, `imx7_csi_setup_vb2_buf()`, `imx7_csi_video_next_buf()`, `imx7_csi_vb2_buf_done()`, and `imx7_csi_fast_track_buffer()`. V4L2 entry points are split across video ioctls, vb2 queue ops, file ops, subdev pad ops, async notifier callbacks, and platform probe/remove.

## Control Flow
Probe allocates `struct imx7_csi`, gets `mclk`, maps MMIO, requests the CSI IRQ, stores model data from OF, initializes the media device and CSI subdev, registers an async notifier for endpoint 0, and later links the bound upstream subdev to the CSI sink pad. The media graph creates a CSI subdev with sink/source pads and a capture video node linked from the source pad.

Format negotiation occurs at both subdev and video-node levels. The subdev sink accepts supported bus codes and propagates size, code, field, and colorimetry to the source pad. The video node chooses a memory FourCC, aligns width to an 8-byte hardware requirement expressed in pixels, derives bytesperline and sizeimage, and stores a fixed compose rectangle. Before streaming, `imx7_csi_video_validate_fmt()` checks that media bus size and YUV/RGB class match the capture node format.

Stream start validates formats, starts the media pipeline, calls the CSI subdev `s_stream(1)`, enables the clock, configures CSI registers for parallel or CSI-2 input, allocates the underrun buffer, primes FB1 and FB2, starts the upstream source, clears FIFO/DMA state, enables interrupts, enables DMA requests, and enables hardware. Each framebuffer completion interrupt chooses FB1 or FB2, returns the completed vb2 buffer if present, fetches the next queued buffer or underrun buffer, writes the hardware base-address register, and increments the frame sequence. Stream stop marks the next EOF as last, waits up to two seconds, disables IRQs and DMA, stops upstream streaming, returns active/queued buffers, resets defaults, and disables the clock.

## State and Persistence
State is runtime-only. The CSI registers, active framebuffer addresses, and coherent underrun buffer are re-created for each stream. The ready queue is protected by `q_lock`; `buf_num`, `active_vb2_buf[]`, and `last_eof` are protected by `irqlock`. The driver uses media graph state to infer whether the upstream source is CSI-2 and to validate stream links. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on V4L2 subdevs, async notifier and fwnode graph bindings, media controller pipeline helpers, videobuf2 DMA-contig, the platform clock named `mclk`, CSI MMIO registers, and an IRQ. It integrates with upstream sensors, muxes, or CSI-2 bridges through media links and stream enable/disable calls. OF compatibles are `fsl,imx8mq-csi`, `fsl,imx7-csi`, and `fsl,imx6ul-csi`.

## Risks and Edge Cases
The two-register DMA scheme has a race when userspace queues a buffer just as hardware switches framebuffers; `imx7_csi_fast_track_buffer()` mitigates this by checking the opposite completion bit but intentionally falls back to the slow path on ambiguity. If both FB1 and FB2 completion bits are set, the handler cannot know which buffer is active and skips updating `buf_num`, which can affect buffer replacement latency. The underrun buffer prevents DMA into invalid memory but can hide userspace starvation as dropped frames. The stop path depends on receiving a final EOF and logs a timeout when hardware or upstream stops unexpectedly. Input format support and YUYV/UYVY packing differ between parallel and CSI-2 paths, making media graph validation important.

## Test Signals
Strong signals include successful async binding and immutable media links, `media-ctl` format propagation, `v4l2-compliance` on the capture node, streaming from parallel and CSI-2 sources, RAW8/10/12/14 and YUV422 8-bit modes, correct width alignment and padded compose reporting, buffer starvation with underrun behavior, fast buffer queuing while streaming, FIFO overflow and HRESP error recovery, stream stop EOF completion, and suspend-like source start/stop ordering through the media pipeline.
