# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7986-eth.c

## Purpose

This MT7986 Ethernet driver registers ethsys plus SGMII0 and SGMII1 gate providers. It supplies FE, GP, WOCPU0/1, and SGMII reference gates.

## Important APIs, types, and functions

Important data includes `sgmii0_clks[]`, `sgmii1_clks[]`, `eth_clks[]`, and descriptors for each compatible. It uses `mtk_clk_simple_probe()`/`remove` for `"mediatek,mt7986-ethsys"`, `"mediatek,mt7986-sgmiisys_0"`, and `"mediatek,mt7986-sgmiisys_1"`.

## Control flow, state, and persistence

Generic probe registers the matched descriptor. SGMII gates use inverted no-setclr at `0xe4`; eth gates use inverted no-setclr at `0x30`. State is gate hardware state and provider registration.

## Dependencies and integration points

Dependencies are MT7986 bindings and MediaTek gate helpers. Parent names refer to topckgen muxes such as `netsys_2x_sel`, `sgm_325m_sel`, `netsys_mcu_sel`, and `top_xtal`. Consumers are Ethernet MAC/switch, WED offload CPUs, and SGMII PHY glue.

## Risks and test signals

Risks include parent-name mismatch, inverted gate polarity, and missing WOCPU clocks for offload. Test Ethernet traffic, SGMII0/1 links, WED offload, and clock summary.
