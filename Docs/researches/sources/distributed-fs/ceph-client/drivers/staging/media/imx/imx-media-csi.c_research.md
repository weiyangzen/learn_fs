# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx-media-csi.c

## Purpose

`imx-media-csi.c` is the i.MX IPUv3 CSI subdevice driver. It negotiates a sink pad plus two source pads, routes incoming parallel/BT.656/MIPI CSI-2 data either directly to VDIC/IC or through SMFC/IDMAC to memory, owns capture-node creation for the IDMAC output, handles EOF interrupts, and supports frame skipping and frame interval monitoring.

## Important APIs, Types, and Functions

`struct csi_priv` contains the V4L2 subdevice, pads, async notifier, capture video device, frame interval monitor, IPU CSI/SMFC/IDMAC handles, active formats and color descriptors, crop/compose rectangles, skip pattern, double-buffered active vb2 buffers, underrun DMA buffer, routing state, IRQs, timer, controls, stream counter, and frame-sequence state.

Key functions include `csi_get_upstream_mbus_config()`, `requires_passthrough()`, `csi_idmac_setup_channel()`, `csi_idmac_start()`, `csi_idmac_stop()`, `csi_start()`, `csi_stop()`, `csi_set_fmt()`, `csi_set_selection()`, `csi_set_frame_interval()`, `csi_link_setup()`, `csi_registered()`, and `imx_csi_probe()`. IRQ handlers are `csi_idmac_eof_interrupt()` and `csi_idmac_nfb4eof_interrupt()`.

## Control Flow

Probe creates the subdevice, initializes three pads, assigns the IPU CSI group id, selects pinctrl, and registers an async notifier for the upstream endpoint. When registered with V4L2, the driver obtains the IPU CSI block, initializes default formats/frame intervals/crop/compose, creates a FIM instance, and registers a legacy capture node on the IDMAC output pad.

Link setup records one upstream source and one downstream sink. Source pad `CSI_SRC_PAD_IDMAC` requires a video node and selects `IPU_CSI_DEST_IDMAC`; source pad `CSI_SRC_PAD_DIRECT` accepts VDIC or IC subdevices. Stream-on asks the upstream entity for its media-bus config, selects the CSI input mux, starts upstream, optionally waits out initial BT.656 frames, starts SMFC/IDMAC for memory capture, programs CSI window/downsize/interface/destination/skip, enables FIM, and finally enables CSI.

IDMAC setup obtains SMFC and IDMAC resources, allocates an underrun buffer, seeds two hardware buffers from queued capture buffers or the underrun buffer, configures CPMEM format or passthrough, burst size, watermark/high-priority behavior, double buffering, and IRQs. EOF IRQ completes the current buffer, advances sequence, loads the next buffer, selects the new hardware buffer, toggles buffer index, and refreshes the timeout timer.

## State and Persistence Behavior

All state is runtime-only. The driver stores active pad formats, crop/compose, frame intervals, selected skip descriptor, active output pad, destination, upstream subdev, downstream sink, stream count, double-buffer state, and fatal/error flags. The lock protects pad/routing/stream state; `irqlock` protects EOF-side state. Hardware resources and coherent underrun memory are acquired on stream start and released on stop.

## Dependencies and Integration Points

CSI depends on platform IPU child data, media-controller graph links, V4L2 async/fwnode discovery, V4L2 subdev pad operations, vb2 capture helper APIs, IPUv3 CSI/SMFC/IDMAC/CPMEM helpers, pinctrl, IRQs, timers, and `imx-media-fim`. It binds into the parent `imx-media` device through group ids and triggers registration of internal IPU subdevices.

## Risks and Edge Cases

Several operations require upstream `get_mbus_config()`; missing support returns an error and blocks negotiation. Passthrough choices are subtle for raw/bayer, 16-bit parallel, and non-UYVY/YUYV 8-bit buses. EOF timeout calls `imx_media_capture_device_error()` and requires a stream restart. The stop path waits for one last EOF before disabling CSI to avoid documented hangs. Cropping for interlaced BT.656 is intentionally constrained. `vc_num` is stored but not clearly set in the visible code path, so virtual-channel routing deserves validation with CSI-2 graphs.

## Test Signals

Test parallel, BT.656/BT.1120, and MIPI CSI-2 inputs; raw passthrough and IPU YUV/RGB conversions; direct links to VDIC/IC; IDMAC capture with queued and underrun buffers; frame skipping ratios; crop/compose downscale by 1/2; interlaced and alternate fields; NFB4EOF marking; EOF timeout; last-EOF streamoff wait; missing upstream mbus-config; and link busy/error behavior.
