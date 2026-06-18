# sources/distributed-fs/ceph-client/drivers/staging/media/ipu7/ipu7-isys-csi2.c

## Purpose
Implements the IPU7 CSI-2 V4L2 subdevice: supported media-bus formats, event subscription, CSI receiver stream enable/disable, crop handling, stream routing, subdevice registration, SOF/EOF event delivery, and remote sensor frame descriptor lookup.

## Important APIs, Types, and Functions
The exported functions are `ipu7_isys_csi2_get_link_freq()`, `ipu7_isys_csi2_init()`, `ipu7_isys_csi2_cleanup()`, `ipu7_isys_csi2_sof_event_by_stream()`, `ipu7_isys_csi2_eof_event_by_stream()`, and `ipu7_isys_csi2_get_remote_desc()`. Internal operations are wired through `csi2_sd_core_ops`, `csi2_sd_pad_ops`, and `csi2_entity_ops`. `csi2_supported_codes[]` is the source list for `enum_mbus_code`. `csi2_irq_enable()` and `csi2_irq_disable()` program per-port legacy error/sync interrupt registers. `ipu7_isys_csi2_enable_streams()` and `ipu7_isys_csi2_disable_streams()` bridge V4L2 stream enablement to receiver power/IRQ setup and the upstream sensor subdevice.

## Control Flow
Initialization stores `isys`, base address, port, and hardware-specific legacy IRQ mask, initializes the shared `ipu7_isys_subdev`, finalizes V4L2 subdev state, and registers it. Stream enable powers the CSI block only on the first active stream, sets APB divider and adapter input mode, optionally enables port A/B aggregation on non-IPU7 hardware, powers the PHY through `ipu7_isys_csi_phy_powerup()`, enables legacy IRQs, resolves the routed upstream sink stream, and calls `v4l2_subdev_enable_streams()` on the remote sensor. Stream disable reverses the upstream call, decrements `stream_count`, and when it reaches zero powers down PHY and disables IRQs.

## State and Persistence Behavior
Persistent driver state is held in `struct ipu7_isys_csi2`: `base`, `port`, `nlanes`, `phy_mode`, `legacy_irq_mask`, `receiver_errors`, and `stream_count`. Crop and format state live in V4L2 subdev active state. SOF events atomically increment `stream->sequence`; EOF is logged but does not change sequence state. Hardware state persists in CSI and GP registers until streamoff or runtime suspend cleanup.

## Dependencies and Integration Points
Depends on media-controller graph helpers, V4L2 subdev streams/routing APIs, CSI PHY helpers, `ipu7-isys-subdev` format/routing helpers, and register constants from `ipu7-isys-csi2-regs.h`. It integrates with `ipu7-isys-video.c` through remote descriptor lookup and source stream metadata, with `ipu7-isys.c` through CSI error/SOF ISR handling, and with sensor drivers through `get_frame_desc` and stream enable operations.

## Risks and Test Signals
Risks include incomplete unwind if upstream stream enable fails after receiver hardware is already enabled, stream-mask handling that selects only the first set bit up to stream 63, zero sync masks that may make direct legacy FS/FE paths inactive, and crop logic allowing only vertical cropping while bayer order conversion still depends on top offset. Test with multiple virtual channels, sensors with and without `get_frame_desc`, bayer crop offsets, IPU7 and IPU7P5 IRQ masks, and repeated stream-on/off cycles watching PHY power and event sequence behavior.
