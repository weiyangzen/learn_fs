# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispcsi2.c

## Purpose
`ispcsi2.c` implements the OMAP3 ISP CSI-2 receiver subdevice. It configures CSI-2 receiver registers, D-PHY timing through the associated PHY, context 0 packet handling, format mapping, IRQ handling, media links to CCDC or memory, and a video-capture node for CSI-2 memory output.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_csi2_init()`, `omap3isp_csi2_cleanup()`, `omap3isp_csi2_register_entities()`, `omap3isp_csi2_unregister_entities()`, `omap3isp_csi2_reset()`, and `omap3isp_csi2_isr()`.
- Receiver configuration: `csi2_if_enable()`, `csi2_recv_config()`, `csi2_ctx_config()`, `csi2_timing_config()`, and `csi2_configure()` program interface, context, timing, frame skipping, ECC, DPCM, and output mode.
- Format mapping: `csi2_ctx_map_format()` uses `__csi2_fmt_map` to map V4L2 media bus formats, DPCM decompression, output destination, and revision 15.0 differences to CSI-2 context format IDs.
- Streaming: `csi2_set_stream()` acquires/releases the PHY, enables SBL writes for memory output, configures hardware, starts context/interface when buffers are available, and handles stop synchronization.
- IRQ/buffer path: `csi2_isr_ctx()` handles frame-end context interrupts and initial frame skipping; `csi2_isr_buffer()` rotates capture buffers; `csi2_queue()` arms the first buffer or restarts from underrun.

## Control Flow
Probe initializes CSI2A for all supported hardware and prepares CSI2C only on revision 15.0, though entity initialization is only performed for CSI2A in this file. Link setup records memory and CCDC output bits and updates video-port-only/clock-enable control flags. On stream start, the PHY is acquired, SBL write is enabled if memory output is active, receiver/context/timing registers are programmed from pipeline bus data, and hardware starts immediately unless memory output has no queued buffer. IRQs clear top-level and context status, mark the pipeline errored on OCP, FIFO, uncorrectable ECC, short packet, or complex IO errors, skip configured initial frames, and rotate memory buffers on frame-end interrupts.

## State And Persistence
Persistent state is held in `struct isp_csi2_device`: active formats, output bitmask, DPCM flag, frame-skip count, PHY pointer, context array, timing array, control config, stream state, stop synchronization, and video queue. Context 0 carries virtual channel, format ID, DPCM predictor, data offsets, ping/pong addresses, and enable state. Hardware register state is volatile and reconstructed on each stream start.

## Dependencies And Integration Points
The file integrates with the V4L2 subdev/media graph, `ispvideo` capture queues, CSI PHY acquire/release/reset paths, ISP SBL write enablement, pipeline clock/rate metadata, sensor bus config and `g_skip_frames`, and format metadata from `omap3isp_video_format_info()`. It uses register definitions from `ispreg.h` and CSI-2 device/types from `ispcsi2.h`.

## Risks And Edge Cases
- Only context 0 is actively configured and handled despite hardware support for multiple contexts.
- `csi2_configure()` can return `-EBUSY` or `-EPIPE`, but `csi2_set_stream()` does not check that return before continuing.
- Frame skip behavior disables the video port by selecting memory-only format mapping until skipped frames are drained; this is hardware-workaround sensitive.
- The memory output path defers hardware start until a buffer is queued, so underrun flag handling is critical.
- CSI2C setup lacks corresponding entity/video cleanup in this file, reflecting partial availability or core-managed use; revision-specific users need care.

## Test Signals
Exercise format mapping for RAW10, RAW10 DPCM8, YUYV, memory-only, CCDC-only, combined output, and revision 15.0 user-defined IDs. Test media link exclusivity, no-buffer start and underrun restart, frame skip countdown, error IRQ propagation to `pipe->error`, PHY reset busy paths, and stop synchronization under active context interrupts.
