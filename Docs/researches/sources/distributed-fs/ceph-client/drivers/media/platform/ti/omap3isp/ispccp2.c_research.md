# sources/distributed-fs/ceph-client/drivers/media/platform/ti/omap3isp/ispccp2.c

## Purpose
`ispccp2.c` implements the TI OMAP3 ISP CCP2/CSI1 receiver media subdevice. It supports sensor input through the CCP2 interface and memory input through the logical channel memory engine, exposes a V4L2 subdevice with sink/source pads, owns a video-output node for memory input, and bridges incoming RAW Bayer data to the CCDC video port.

## Important APIs, Types, And Functions
- Public entry points: `omap3isp_ccp2_init()`, `omap3isp_ccp2_cleanup()`, `omap3isp_ccp2_register_entities()`, `omap3isp_ccp2_unregister_entities()`, and `omap3isp_ccp2_isr()`.
- Stream lifecycle: `ccp2_s_stream()` handles `ISP_PIPELINE_STREAM_CONTINUOUS`, `ISP_PIPELINE_STREAM_SINGLESHOT`, and stopped states, including CSI PHY acquisition/release, SBL read enable, and hardware enable/disable.
- Hardware configuration: `ccp2_reset()`, `ccp2_pwr_cfg()`, `ccp2_phyif_config()`, `ccp2_vp_config()`, `ccp2_lcx_config()`, and `ccp2_mem_configure()` program CCP2 control, logical channel, video port, and memory-channel registers.
- Format operations: `ccp2_try_format()`, `ccp2_enum_mbus_code()`, `ccp2_enum_frame_size()`, `ccp2_get_format()`, and `ccp2_set_format()` constrain supported sink formats to `SGRBG10` and `SGRBG10_DPCM8`, force the source to uncompressed `SGRBG10`, and propagate sink-to-source dimensions.
- Media/video hooks: `ccp2_link_setup()` records whether the sink is fed from memory or a sensor and whether the source feeds CCDC; `ccp2_video_queue()` writes the DMA input address for memory input.

## Control Flow
Initialization sets up wait queues, revision-specific regulator/PHY references, media pads, the V4L2 subdev, a video-output queue, default formats, and then resets the module. Continuous streaming acquires the CSI PHY when present, configures sensor-facing physical/logical-channel registers from `isp_bus_cfg`, prints register status, and enables all logical channels plus interface mode. Single-shot streaming configures memory read parameters from the sink format, enables the CSI1 read SBL path, and enables the memory channel. Stopping synchronizes with in-flight hardware through `omap3isp_module_sync_idle()`, disables the appropriate interface, disables SBL for memory input, and releases the PHY for sensor input.

## State And Persistence
Persistent runtime state lives in `struct isp_ccp2_device`: active pad formats, input/output selection, cached logical-channel and memory-channel configuration, `video_in`, optional `phy`, optional `vdds_csib` regulator, stream state, stop wait queue, and stopping atomic. Register state is volatile hardware state restored on stream configure rather than saved across power loss. DMA addresses are per-buffer state written on queue and EOF interrupts.

## Dependencies And Integration Points
This file depends on the ISP core register helpers, pipeline state helpers, V4L2/media entity APIs, `ispvideo` queues, CSI PHY management, SBL enable/disable, sensor bus configuration via `v4l2_subdev_to_bus_cfg()`, and sensor callbacks such as `g_skip_top_lines`. It integrates with CCDC through the media graph and video port, with memory input through the local video-output node, and with platform power through `vdds_csib` on older revisions.

## Risks And Edge Cases
- `ccp2_s_stream()` calls `ccp2_if_configure()` without checking its return value in the continuous path, so a failed bus/PHY configuration can be followed by interface enable.
- Link setup uses a documented hack that encodes remote entity type into the local pad index; graph changes could break input/output classification.
- Memory read alignment is special: line length and padded line length need 32-byte handling despite underlying 128-bit constraints.
- Revision-specific video-port divisor encoding differs substantially between OMAP3430-style and revision 15.0 hardware.
- Error IRQ handling marks the pipeline error but otherwise leaves recovery to the broader pipeline.

## Test Signals
Useful signals include media graph link validation for memory versus sensor input exclusivity, V4L2 format enumeration/clamping tests, stream start/stop tests for both continuous and single-shot paths, regulator and PHY acquire/release failure injection, EOF buffer-rotation tests, and IRQ error tests verifying `pipe->error` is set for LCx and OCP errors.
