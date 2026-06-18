# sources/distributed-fs/ceph-client/drivers/media/platform/aspeed/aspeed-video.c

## Purpose
This platform driver exposes the ASPEED AST2400/AST2500/AST2600 video engine as a V4L2 capture device for BMC screen capture. It detects host VGA or BMC graphics input timings, captures into internal DMA source buffers, compresses frames as standard JPEG or ASPEED-specific JPEG, and delivers compressed frames through a videobuf2 DMA-contiguous queue.

## Important APIs, Types, and Functions
`struct aspeed_video` owns MMIO, clocks, reset, SCU/GFX regmaps, V4L2/vb2 objects, source/JPEG/BCD DMA buffers, timing state, controls, and stream flags. Key helpers are `aspeed_video_start_frame()`, `aspeed_video_irq()`, `aspeed_video_get_resolution_vga()`, `aspeed_video_set_resolution()`, `aspeed_video_update_regs()`, `aspeed_video_start_streaming()`, and `aspeed_video_setup_video()`. It implements V4L2 ioctls for formats, inputs, stream parameters, DV timings, and source-change events, plus controls for JPEG quality, chroma subsampling, ASPEED HQ mode, and HQ quality.

## Control Flow
Probe maps the VE registers, reads SoC variant config, requests the interrupt, prepares clocks, allocates the JPEG header DMA table, and registers one video node. The first open powers the engine, initializes registers, detects the current resolution, and sizes DMA buffers. `STREAMON` updates compression registers and starts a frame from the queued vb2 list. Compression-complete IRQs finish the current buffer, update sequence/timestamps, swap source buffers for ASPEED JPEG delta mode, and start the next frame if streaming continues. Mode-detect watchdog IRQs reset the engine, error all queued buffers, and schedule delayed resolution work; the work item re-detects timings, emits a V4L2 source-change event when dimensions change, or restarts capture.

## State and Persistence
All state is volatile driver and hardware state. The driver persists no settings across module unload or reboot. `flags` coordinates clocks, streaming, frame-in-progress, resolution detection, and stopped state. `video_lock` serializes V4L2/vb2 operations; `lock` protects the buffer list in IRQ context. DMA state includes two source buffers, a JPEG table buffer, and an optional BCD buffer used for ASPEED JPEG change detection. Runtime controls mutate register state while streaming.

## Dependencies and Integration Points
The driver depends on platform OF compatibles, `eclk`/`vclk`, reset controls, optional reserved memory, 32-bit coherent DMA, ASPEED SCU and GFX syscon regmaps, V4L2 controls/events/DV timings, and `videobuf2-dma-contig`. It uses `uapi/linux/aspeed-video.h` for ASPEED-specific input and pixel-format controls. Debugfs can expose capture/compression/performance state.

## Risks and Edge Cases
Resolution detection depends on stable sync and pixel clock; no-signal paths fall back to minimum timings and return `-ENOLINK` from query timings. Stop waits for `VIDEO_FRAME_INPRG`; timeout forces reset and register reinitialization. Standard JPEG deliberately keeps the last buffer queued when it is the only buffer, which differs from ASPEED JPEG buffer consumption. Input switching requires SCU/GFX regmaps and is rejected while vb2 is busy. Source buffer allocation failures leave capture unable to proceed. Small VGA modes use sync mode because direct fetch lacks interrupts below the threshold.

## Test Signals
Build with AST2400, AST2500, and AST2600 compatibles. Exercise open/close, `VIDIOC_QUERYCAP`, JPEG/AJPG format selection, input switching, `VIDIOC_QUERY_DV_TIMINGS`, nonblocking resolution-change behavior, controls during streaming, and vb2 MMAP/DMABUF/READ capture. Hardware tests should cover no signal, resolution changes, VGA versus GFX input, stop timeout recovery, debugfs output, and DMA buffer sizing at 640x480 through 1920x1200.
