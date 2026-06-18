<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile

Purpose: Maps MediaTek PHY Kconfig symbols to compiled objects and aggregate driver modules.

Important APIs and types: Defines Kbuild object assignments for DP, PCIe, T-PHY, UFS, XS-PHY, XFI T-PHY, HDMI, MIPI CSI, and MIPI DSI drivers. Aggregate objects are `phy-mtk-hdmi-drv` and `phy-mtk-mipi-dsi-drv`.

Control flow: Kbuild includes simple one-file objects when corresponding configs are enabled. HDMI builds common glue plus MT2701, MT8173, and MT8195 implementations into one module. MIPI DSI builds common glue plus MT8173 and MT8183 implementations into one module.

State and persistence: No runtime state. The build graph determines which symbols are linked together and which OF match data is available at runtime.

Dependencies and integration points: Coupled to `Kconfig` symbols and exported configuration structures declared in local headers. The aggregate object names determine module output names.

Risks: Omitting a SoC-specific object from an aggregate driver breaks OF match data or external config symbols at link time. Adding new compatibles requires updating both Kconfig dependencies, if needed, and this Makefile.

Test signals: Module and built-in builds for each config, link checks for HDMI/MIPI aggregate objects, and `modinfo` verifying expected aliases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/Makefile -->
