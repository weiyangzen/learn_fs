# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/sun6i_mipi_csi2.c

Purpose: implements the Allwinner A31 MIPI CSI-2 receiver as a V4L2 async subdevice bridge with runtime PM, regmap configuration, D-PHY control, sensor binding, and media links.

Important APIs and functions: module entry is `module_platform_driver(sun6i_mipi_csi2_platform_driver)`. Key paths include format lookup, controller enable/disable/configure, `sun6i_mipi_csi2_s_stream`, subdev pad enum/get/set/init, async notifier bound/source setup, bridge setup/cleanup, resources setup/cleanup, runtime suspend/resume, and probe/remove.

Control flow: probe maps registers through `devm_regmap_init_mmio_clk`, gets the module clock, reserves a 297 MHz clock rate, gets shared reset and external D-PHY, initializes the PHY, enables runtime PM, then registers the bridge subdevice and optional sensor notifier. When a remote sensor binds, the driver creates an immutable link from sensor source pad to CSI-2 sink and stores `source_subdev`. On stream start, it resumes PM, reads the upstream sensor `V4L2_CID_PIXEL_RATE`, computes MIPI D-PHY timing from pixel rate, bits-per-pixel, and lane count, resets/configures the PHY, writes controller reset/version/unpack/config/VC-DT registers, enables the controller, powers the PHY, and starts the sensor. Stream stop stops the sensor, powers off the PHY, disables the controller, and drops PM.

State and persistence: `struct sun6i_mipi_csi2_device` stores regmap, clock, reset, external PHY, and bridge state. The active mbus format and parsed lane endpoint persist in the bridge. Hardware state is reconstructed per stream start and lost across runtime suspend.

Dependencies and integration points: depends on media CSI-2 data type constants, V4L2 control API for pixel rate, V4L2 async/fwnode, generic PHY MIPI D-PHY helpers, regmap, runtime PM, and an external `dphy` provider. Its source pad is intended to feed the sun6i CSI bridge MIPI input.

Risks: only RAW8/RAW10 Bayer formats are supported. Missing or zero `V4L2_CID_PIXEL_RATE` prevents streaming. Only virtual channel 0 is effectively configured for use. D-PHY clock-rate debug output accounts for DDR manually but does not alter the generic helper result. If no sensor endpoint exists, the subdevice still registers but has no source and returns `-ENODEV` on stream.

Test signals: media graph binding to a sensor and sun6i CSI, stream start with valid pixel-rate control, lane-count parsing, D-PHY configure/power sequencing, register dumps around version-enable toggling, and negative tests for missing source or pixel rate.
