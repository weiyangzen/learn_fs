<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c -->
# sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c

Purpose: Provides common MediaTek HDMI PHY platform glue. It maps registers, registers the HDMI PLL clock, creates the generic PHY, reads common DT tuning properties, and dispatches to SoC-specific operations.

Important APIs and types: `to_mtk_hdmi_phy()` converts clock hardware to driver state. Common PHY callbacks are `mtk_hdmi_phy_power_on()`, `mtk_hdmi_phy_power_off()`, and `mtk_hdmi_phy_configure()`. Probe uses `struct mtk_hdmi_phy_conf` function pointers and optional regulator descriptor.

Control flow: Probe allocates state, maps registers, gets `pll_ref`, reads `clock-output-names`, loads OF match data, registers the PLL clock, reads `mediatek,ibias` and `mediatek,ibias_up`, installs default impedance values, creates a PHY with ops only when enable/disable callbacks exist, registers a PHY provider, optionally disables TMDS by default, optionally registers a fixed regulator, and registers the clock provider. Power-on enables the PLL clock then calls SoC TMDS enable; power-off disables TMDS then the clock. Configure delegates to SoC callback when present.

State and persistence: Stores MMIO base, device, SoC config, PLL clock, regulator device, PLL rate, impedance, ibias values, and MT8195 TMDS ratio flag. Devm resources handle lifetime.

Dependencies and integration points: Integrates generic PHY, clk provider, OF match data, regulator core, and SoC files for MT2701/MT8173/MT8195.

Risks: `mtk_hdmi_phy_dev_get_ops()` can return NULL if config callbacks are incomplete, making probe fail via `devm_phy_create()`. Required DT properties `mediatek,ibias` and `mediatek,ibias_up` are common even if a SoC might not use both. Clock provider registration is not devm-managed.

Test signals: Probe each compatible, PLL clock consumer set-rate, PHY power cycles, optional MT8195 regulator registration, missing DT property failures, and display hotplug/mode-set sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/phy/mediatek/phy-mtk-hdmi.c -->
