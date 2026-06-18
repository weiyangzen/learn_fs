# sources/distributed-fs/ceph-client/drivers/net/ethernet/stmicro/stmmac/stmmac_pcs.c

Purpose: integrated PCS implementation for STMMAC/DWMAC MACs. It presents SGMII and BASE-X hardware PCS state to phylink through `phylink_pcs_ops`, handles PCS interrupts, and exposes PHY interface selection.

Important APIs and functions: `stmmac_integrated_pcs_init()` allocates and installs `struct stmmac_pcs`. `dwmac_integrated_pcs_inband_caps()` reports BASE-X in-band negotiation when TBI/RTBI is supported. `dwmac_integrated_pcs_enable/disable()` toggle MAC interrupt bits through `stmmac_mac_irq_modify()`. `dwmac_integrated_pcs_get_state()` decodes either C22-style BASE-X state or RGSMII status bits. `dwmac_integrated_pcs_config()` writes advertisement and AN control through `dwmac_ctrl_ane()`. `stmmac_integrated_pcs_irq()` accounts AN/link interrupts and notifies phylink.

Control flow: initialization resolves PCS and RGSMII register pointers from offsets, assigns ops, detects TBI/RTBI from `BMSR_ESTATEN`, marks SGMII and 1000BASE-X supported, optionally marks 2500BASE-X from platform SerDes flags, and stores the PCS in `priv->integrated_pcs`. Phylink then calls ops for enable, disable, state, config, and restart. MAC IRQ handlers call `stmmac_integrated_pcs_irq()`.

State and persistence: `struct stmmac_pcs` is devm-allocated and retained by `stmmac_priv`. It stores register bases, masks, the embedded `phylink_pcs`, and `support_tbi_rtbi`. Hardware link/AN state is read on demand. IRQ counters persist in extra stats.

Dependencies and integration: phylink, MII bit definitions, STMMAC MAC IRQ helpers, `priv->hw->reverse_sgmii_enable`, and core-specific PCS offsets from DWMAC core files. `stmmac_main.c` selects the integrated PCS when the requested interface is supported.

Risks and test signals: TBI/RTBI inference from extended status can misclassify unusual hardware. RGSMII decode depends on correct offsets and masks. Test with phylink SGMII/1000BASE-X/2500BASE-X links, in-band AN, AN restart, PCS interrupts, and link speed/duplex reporting.
