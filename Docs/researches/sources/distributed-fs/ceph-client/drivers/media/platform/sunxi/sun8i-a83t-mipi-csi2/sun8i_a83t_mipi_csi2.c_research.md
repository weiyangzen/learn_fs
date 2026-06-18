# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/sun8i_a83t_mipi_csi2.c

Purpose: implements the Allwinner A83T MIPI CSI-2 receiver bridge and coordinates the integrated D-PHY, clocks, reset, runtime PM, sensor async binding, and stream-time controller programming.

Important APIs and functions: module entry is `module_platform_driver(sun8i_a83t_mipi_csi2_platform_driver)`. Key functions include format lookup, `sun8i_a83t_mipi_csi2_init`, enable/disable/configure, `sun8i_a83t_mipi_csi2_s_stream`, pad operations, async notifier bound/source setup, bridge setup/cleanup, suspend/resume, resources setup/cleanup, and probe/remove.

Control flow: probe maps registers with regmap, gets module/MIPI/misc clocks, reserves the module rate at 297 MHz, gets shared reset, registers the integrated D-PHY, enables runtime PM, and registers the bridge subdevice plus optional upstream sensor notifier. Runtime resume deasserts reset, enables all three clocks, and writes BSP-derived initialization values including reserved hardware-lock registers. Stream start resumes PM, obtains upstream pixel rate, computes D-PHY options from pixel rate/bpp/lane count, resets/configures the PHY, writes controller reset/config/VC-DT registers, enables sync, powers on the PHY, and starts the source subdevice. Stop reverses source, PHY, controller, and PM.

State and persistence: `struct sun8i_a83t_mipi_csi2_device` stores regmap, clocks, reset, integrated PHY, and bridge state. Active mbus format, parsed endpoint, and source subdev persist in the bridge. Controller magic initialization is repeated on runtime resume.

Dependencies and integration points: depends on V4L2 async/fwnode, media-controller subdevs, V4L2 pixel-rate control, generic PHY MIPI D-PHY helpers, regmap, common clocks, reset, and the local D-PHY provider. The source pad feeds downstream CSI/ISP media graph entities.

Risks: only RAW8/RAW10 Bayer formats are supported. Several magic register values come from BSP behavior and are required to avoid unsolicited interrupts, but their semantics are not fully known. Only virtual channel 0 is configured for real payload use. Stream start fails if the upstream sensor lacks pixel rate or lane count. Cleanup calls `phy_exit` although the PHY was created by the local provider, so lifetime assumptions should be checked against generic PHY semantics.

Test signals: A83T media graph binding, runtime resume register initialization, sensor stream with valid pixel rate, D-PHY power sequencing, RAW8/RAW10 capture, stream stop/restart, and negative tests for missing graph endpoint.
