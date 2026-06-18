<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h

Purpose: Declares the common MediaTek HDMI PHY data structures and SoC configuration symbols shared by common and SoC-specific HDMI PHY files.

Important APIs and types: `struct mtk_hdmi_phy_conf` contains clock flags, default-off behavior, optional regulator descriptor, clock ops, TMDS enable/disable callbacks, and optional configure callback. `struct mtk_hdmi_phy` stores MMIO, device, config, PLL clock/hw, regulator, cached rate, impedance, ibias, and high-TMDS flag. Exports `to_mtk_hdmi_phy()` and three SoC config objects.

Control flow: No runtime logic in the header. It defines the interface by which SoC files provide clock and analog operations to `phy-mtk-hdmi.c`.

State and persistence: The state struct fields are live runtime state owned by the common probe and SoC callbacks. Cached PLL and TMDS state can influence later configure/prepare operations.

Dependencies and integration points: Includes clk, phy, platform, module, syscon, regulator, and type headers. Shared by MT2701, MT8173, MT8195, and common glue.

Risks: Adding fields or callbacks affects all SoC implementations. Optional callback semantics must remain clear, especially configure and regulator support.

Test signals: Compile/link of aggregate HDMI module, all OF match data resolving to declared configs, and callback presence validation in common probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.h -->
