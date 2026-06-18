# sources/distributed-fs/ceph-client/drivers/media/platform/sunxi/sun8i-a83t-mipi-csi2/Makefile

Purpose: links the A83T MIPI CSI-2 receiver and its integrated D-PHY helper into one module.

Important APIs and entries: `sun8i-a83t-mipi-csi2-y` contains `sun8i_a83t_mipi_csi2.o` and `sun8i_a83t_dphy.o`; `obj-$(CONFIG_VIDEO_SUN8I_A83T_MIPI_CSI2)` emits the composite object.

Control flow: kbuild includes both controller and PHY provider code whenever the option is enabled.

State and persistence: no runtime state.

Dependencies and integration points: keeps the integrated PHY provider in the same module as the controller that owns its registers.

Risks: separating the D-PHY without adjusting module ownership would break resource sharing through `struct sun8i_a83t_mipi_csi2_device`.

Test signals: module build with both objects linked and no unresolved `sun8i_a83t_dphy_register`.
