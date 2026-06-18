# sources/distributed-fs/ceph-client/drivers/media/platform/microchip/microchip-csi2dc.c

## Purpose
`microchip-csi2dc.c` implements the Microchip SAMA7G5 CSI2 Demux Controller as a V4L2 subdevice and media bridge. It accepts MIPI CSI-2 or parallel/BT.656 input, configures the CSI2DC video pipe, and exposes a sink/source media entity to downstream capture blocks.

## Important APIs, Types, and Functions
`struct csi2dc_device` stores MMIO base, clocks, current format, media pads, async notifier, remote subdevice, and bus-mode flags. `struct csi2dc_format` maps V4L2 media-bus codes to CSI-2 data types. Pad operations are `csi2dc_enum_mbus_code()`, `csi2dc_get_fmt()`, and `csi2dc_set_fmt()`. Streaming and hardware setup use `csi2dc_power()`, `csi2dc_get_mbus_config()`, `csi2dc_vp_update()`, and `csi2dc_s_stream()`. Probe and graph setup are handled by `csi2dc_of_parse()`, `csi2dc_prepare_notifier()`, `csi2dc_async_bound()`, and `csi2dc_probe()`.

## Control Flow
Probe maps registers, acquires `pclk` and `scck`, initializes the subdevice and media pads, parses input/output endpoints, registers an async notifier for the upstream sensor or bridge, powers the hardware briefly to read the version, enables runtime PM, then registers the subdevice. Format negotiation only allows setting the sink pad and propagates the selected format to the source pad. On stream start, runtime PM resumes clocks, the remote bus configuration is read when available, `csi2dc_vp_update()` programs parallel or serial pipe registers, and the upstream subdevice is started. Stream stop turns off the upstream subdevice and releases runtime PM.

## State and Persistence
Runtime state is in `csi2dc_device`: current active media-bus format, current data type, virtual channel, clock-continuity mode, media graph links, and whether the video pipe/source pad exists. Hardware state is volatile MMIO programming in `GCFG`, `VPCFG`, `VPE`, and `PU`. No persistent storage exists.

## Dependencies and Integration Points
The driver depends on V4L2 subdevice APIs, async notifiers, fwnode graph parsing, runtime PM, COMMON_CLK, and MMIO resources. It integrates upstream with a sensor/CSI source and downstream with a parallel/BT.656 consumer such as XISC. DT compatible is `microchip,sama7g5-csi2dc`.

## Risks and Edge Cases
The loop in `csi2dc_set_fmt()` increments `fmt` inside and outside the `for` body, but only `try_fmt` is retained, so future edits should avoid assuming `fmt` remains sequential. `csi2dc_get_mbus_config()` logs failure but returns success, meaning stale DT clock-continuity flags may be used. The probe error path after enabling runtime PM does not explicitly power down before notifier cleanup, so runtime-PM lifetime should be checked during changes. Parallel mode bypasses serial video-pipe programming and only sets `GPIOSEL`.

## Test Signals
Test graph probing with and without an output endpoint, RAW8/RAW10/YUYV format propagation, MIPI continuous and non-continuous clock modes, parallel and BT.656 endpoints, runtime suspend/resume around streaming, and successful media links from upstream entity to CSI2DC sink and CSI2DC source to the capture consumer.
