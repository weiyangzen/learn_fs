# sources/distributed-fs/ceph-client/drivers/staging/media/imx/imx6-mipi-csi2.c

## Purpose

`imx6-mipi-csi2.c` implements the i.MX6 MIPI CSI-2 receiver bridge subdevice. It exposes one sensor sink pad and four virtual-channel source pads, configures the DesignWare CSI-2 D-PHY/controller, handles fwnode async binding to the upstream sensor, and forwards a single negotiated media-bus format to all source pads.

## Important APIs, Types, and Functions

`struct csi2_dev` stores the subdevice, async notifier, five pads, D-PHY/reference/pixel clocks, MMIO base, remote source subdevice and pad, configured data lanes, mutex, active format, stream count, active source, and source-pad link bitmap. Important functions include `csi2_start()`, `csi2_stop()`, `csi2_s_stream()`, `csi2_link_setup()`, `csi2_set_fmt()`, `csi2_registered()`, `csi2_async_register()`, and `csi2_probe()`.

Hardware helpers include `csi2_enable()`, `csi2_set_lanes()`, `dw_mipi_csi2_phy_write()`, `csi2_dphy_init()`, `csi2_dphy_wait_stopstate()`, `csi2_dphy_wait_clock_lane()`, `csi2ipu_gasket_init()`, and `csi2_get_active_lanes()`.

## Control Flow

Probe initializes the subdevice, pads, clocks, MMIO, mutex, enables reference and D-PHY clocks, parses endpoint lane count, creates an async remote sensor match, and registers the subdevice. On bound, it records the remote source pad and creates fwnode links to the CSI-2 sink.

Stream-on requires a linked upstream source and at least one enabled source pad. It enables the pixel clock, programs the CSI2IPU gasket for YUYV ordering when needed, derives D-PHY hs-freq-range from the source `V4L2_CID_LINK_FREQ` or a default 849 Mbps/lane, chooses active lane count from remote mbus config, deasserts CSI-2 resets, asks the sensor to enter manual LP-11 pre-stream state, waits for LP-11, starts upstream streaming, and waits for clock-lane high-speed activity. Streamoff stops upstream, calls `post_streamoff`, asserts resets, and disables the pixel clock.

## State and Persistence Behavior

State is volatile and protected by `lock`. The active format is shared by all pads; source pads mirror sink format. `stream_count` reference-counts nested stream users. Reference and D-PHY clocks stay enabled for the registered device lifetime, while pixel clock is enabled only while streaming.

## Dependencies and Integration Points

The driver depends on platform OF matching (`fsl,imx6-mipi-csi2`), V4L2 fwnode endpoint parsing, V4L2 async notifier, media-controller links, subdev pre/post stream hooks, clocks, MMIO polling, and IMX format initialization helpers. Downstream CSI devices are linked by common imx-media completion code.

## Risks and Edge Cases

If the source lacks `V4L2_CID_LINK_FREQ`, the default D-PHY frequency may be wrong for some sensors. LP-11 wait timeout only warns, but capture may fail later. Clock-lane timeout is fatal. `v4l2_set_subdevdata(&csi2->sd, &pdev->dev)` stores the device pointer rather than `csi2`; local callbacks use container-of on `sd`, so this is only risky for external users of subdevdata. Multiple source pads can be enabled independently but all share one format and one upstream stream.

## Test Signals

Test endpoint parsing for lane counts, remote mbus lane overrides, link-frequency-based D-PHY selection, missing link-frequency default, YUYV gasket programming, LP-11 warning path, clock-lane timeout cleanup, source-pad link requirements, stream reference counting, and remove cleanup of notifier/clocks/media entity.
