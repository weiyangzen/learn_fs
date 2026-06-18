# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun6i-mipi-csi2/Kconfig

Purpose: defines the build option for the Allwinner A31/V3 MIPI CSI-2 receiver bridge driver.

Important APIs and symbols: `VIDEO_SUN6I_MIPI_CSI2` is a tristate depending on V4L platform/video support, sunxi or compile-test, PM, common clock, reset, and `PHY_SUN6I_MIPI_DPHY`. It selects media controller, V4L2 subdevice API, V4L2 fwnode, generic MIPI D-PHY helpers, and regmap MMIO.

Control flow: enabling the option builds the single-object `sun6i-mipi-csi2` driver.

State and persistence: build configuration only.

Dependencies and integration points: ties the CSI-2 bridge to an external sun6i MIPI D-PHY provider and the media-controller graph.

Risks: the hard dependency on `PHY_SUN6I_MIPI_DPHY` means the receiver is not available unless the external PHY driver is enabled. It supports only the formats implemented in the C file.

Test signals: Kconfig selection should pull generic D-PHY helpers and regmap; module build should work under `COMPILE_TEST`.
