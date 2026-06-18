# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7622-eth.c

## Purpose

This MT7622 Ethernet clock driver registers ethsys gates, sgmiisys gates, and an ethsys reset controller. It supports HSDMA, Ethernet switch/GMAC paths, and SGMII reference/feedback clocks.

## Important APIs, types, and functions

Important data includes `eth_cg_regs`, `sgmii_cg_regs`, `eth_clks[]`, `sgmii_clks[]`, `clk_rst_desc`, `eth_desc`, and `sgmii_desc`. The OF table maps `"mediatek,mt7622-ethsys"` and `"mediatek,mt7622-sgmiisys"` to the appropriate descriptor for `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers either ethsys or sgmiisys based on match data. Ethsys also exposes a simple reset bank at `0x34`. Gates use inverted no-setclr semantics with status/set/clear all at `0x30` or `0xe4`. State is hardware gate/reset state and provider registration.

## Dependencies and integration points

Dependencies are MT7622 bindings, `clk-gate.h`, `clk-mtk.h`, and reset support via descriptor. Topckgen parents include `eth_sel`, `eth_500m`, `txclk_src_pre`, `ssusb_tx250m`, `ssusb_eq_rx250m`, `ssusb_cdr_ref`, and `ssusb_cdr_fb`. Consumers include Ethernet MAC, switch, HSDMA, and SGMII PHY glue.

## Risks and test signals

Risks include inverted gate polarity and reset bank misbinding. Test Ethernet link up, switch traffic, SGMII link negotiation, HSDMA, and reset-controller users.
