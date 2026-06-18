# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7988-eth.c

## Purpose

This MT7988 Ethernet driver registers ethdma, SGMII0, SGMII1, and ethwarp clock providers, plus an ethwarp reset controller. It covers XGP/GP/FE/ESW/crypto gates and WOCPU gates for Ethernet offload.

## Important APIs, types, and functions

Important data includes `ethdma_clks[]`, `sgmii0_clks[]`, `sgmii1_clks[]`, `ethwarp_clks[]`, `ethwarp_rst_desc`, and descriptors `ethdma_desc`, `sgmii0_desc`, `sgmii1_desc`, and `ethwarp_desc`. The OF table handles `"mediatek,mt7988-ethsys"`, `"mediatek,mt7988-sgmiisys0"`, `"mediatek,mt7988-sgmiisys1"`, and `"mediatek,mt7988-ethwarp"`.

## Control flow, state, and persistence

Generic simple probe registers the descriptor selected by compatible. Ethdma gates use inverted no-setclr register `0x30`, SGMII gates use `0xe4`, and ethwarp gates use `0x14`. Ethwarp exposes reset offset `0x8` with index map `MT7988_ETHWARP_RST_SWITCH -> bit 9`. State is gate/reset hardware state and provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, `reset.h`, MT7988 clock bindings, and reset bindings. Parent clocks include `netsys_2x_sel`, `netsys_gsw_sel`, `eip197_sel`, `netsys_mcu_sel`, and `top_xtal`. Consumers are Ethernet DMA/switch, SGMII PHY glue, crypto offload, and WED/WOCPU firmware paths.

## Risks and test signals

Risks include wrong reset mapping, parent-name mismatch with topckgen, and inverted gate polarity. Test XGMAC/SGMII links, Ethernet switch traffic, crypto offload, WED/WOCPU boot, and reset-controller operation.
