# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-csi/Kconfig

Purpose: defines the build option for the Allwinner A31-family CSI bridge/capture driver.

Important APIs and symbols: `VIDEO_SUN6I_CSI` is a tristate depending on platform media, video, sunxi or compile-test, PM, common clock, reset, and DMA support. It selects media controller, V4L2 subdevice API, videobuf2 DMA-contig, V4L2 fwnode, and regmap MMIO.

Control flow: selecting this symbol causes the Makefile to link `sun6i-csi.o` from core, bridge, and capture objects.

State and persistence: build configuration only. Runtime state is owned by `struct sun6i_csi_device`.

Dependencies and integration points: enables an A31 CSI block found on A83T, H3, V3/V3s, and A64, with optional ISP integration handled at runtime.

Risks: the driver requires PM, clocks, reset, DMA, and regmap; platform data or device tree omissions surface at probe time.

Test signals: Kconfig dependency resolution, module build, and compile-test builds with `REGMAP_MMIO` selected.
