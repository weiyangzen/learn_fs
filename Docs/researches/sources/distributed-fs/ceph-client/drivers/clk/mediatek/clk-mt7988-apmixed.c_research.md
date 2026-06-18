# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-apmixed.c

## Purpose

This MT7988 apmixedsys driver registers a larger PLL set for networking, memory, multimedia, audio, WED MCU, SGMII/USXGMII, CPU, CCI, and MSDC. It is a built-in PLL provider for MT7988.

## Important APIs, types, and functions

Important definitions are `MT7988_PCW_CHG_BIT`, the `PLL()` macro, `plls[]`, `clk_mt7988_apmixed_probe()`, and compatible `"mediatek,mt7988-apmixedsys"`. The driver uses `mtk_clk_register_plls()`, `mtk_clk_unregister_plls()`, and `of_clk_add_hw_provider()`.

## Control flow, state, and persistence

Probe allocates onecell data sized by the PLL array, registers PLLs, publishes the provider, and unwinds PLLs/data on failure. PLL definitions include reset-bar masks, PCW change registers, optional tuner fields for APLL2, parent `"clkxtal"`, and `MT7988_PCW_CHG_BIT`. State is PLL hardware programming and CCF registration.

## Dependencies and integration points

Dependencies include MT7988 clock bindings, `clk-pll.h`, and MediaTek clock helpers. Topckgen and subsystem drivers consume names such as `netsyspll`, `mpll`, `mmpll`, `apll2`, `net1pll`, `net2pll`, `wedmcupll`, `sgmpll`, `arm_b`, `ccipll2_b`, `usxgmiipll`, and `msdcpll`.

## Risks and test signals

Risks include PCW change-bit mistakes, reset-bar bit shifts, and PLL ID density assumptions. Test topckgen rates, CPU/CCI clocks, Ethernet/USXGMII, eMMC/MSDC, audio, and cleanup on provider failure paths.
