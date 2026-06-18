# sources/distributed-fs/ceph-client/drivers/media/platform/synopsys/Kconfig

Purpose: aggregates Synopsys media platform driver configuration and defines the DesignWare MIPI CSI-2 receiver option.

Important APIs and symbols: sources `drivers/media/platform/synopsys/hdmirx/Kconfig` and defines `VIDEO_DW_MIPI_CSI2RX`, a tristate for the Synopsys DesignWare MIPI CSI-2 Receiver. It depends on Rockchip or compile-test, `VIDEO_DEV`, `V4L_PLATFORM_DRIVERS`, PM, and common clock; it selects generic MIPI D-PHY helpers, media controller, V4L2 fwnode, and V4L2 subdevice API.

Control flow: Kconfig first includes the HDMI RX child config, then exposes the CSI-2 receiver option. Selecting the option causes the sibling Makefile to build `dw-mipi-csi2rx.o`.

State and persistence: build configuration only.

Dependencies and integration points: integrates a generic Synopsys CSI-2 bridge used on Rockchip SoCs with external C-PHY/D-PHY and downstream VICAP-style capture blocks.

Risks: the option is Rockchip-scoped despite being a Synopsys IP block; other SoC users need dependency updates. External PHY and downstream capture integration are required at runtime even though not expressed as direct Kconfig dependencies.

Test signals: menu visibility under Rockchip and `COMPILE_TEST`, module build, and media graph binding with external PHY and downstream capture.
