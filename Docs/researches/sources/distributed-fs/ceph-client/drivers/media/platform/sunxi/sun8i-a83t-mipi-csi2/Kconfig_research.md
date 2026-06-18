# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Kconfig

Purpose: defines the build option for the Allwinner A83T MIPI CSI-2 receiver plus integrated D-PHY driver.

Important APIs and symbols: `VIDEO_SUN8I_A83T_MIPI_CSI2` is a tristate depending on V4L platform/video support, sunxi or compile-test, PM, common clock, and reset. It selects media controller, V4L2 subdevice API, V4L2 fwnode, regmap MMIO, generic PHY, and generic MIPI D-PHY helpers.

Control flow: selecting the symbol builds a composite module containing the CSI-2 receiver and D-PHY provider.

State and persistence: build configuration only.

Dependencies and integration points: unlike the A31 driver, it provides its own D-PHY through the generic PHY framework.

Risks: it has no external PHY dependency, but device-tree consumers must still wire the integrated PHY provider correctly. Format support is limited to RAW8/RAW10 Bayer.

Test signals: Kconfig dependency selection, module build, and PHY provider registration on A83T-compatible nodes.
