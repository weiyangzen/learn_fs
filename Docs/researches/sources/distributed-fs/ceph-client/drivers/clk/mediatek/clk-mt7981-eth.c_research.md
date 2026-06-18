# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7981-eth.c

## Purpose

This MT7981 Ethernet clock driver registers ethsys and two SGMII system providers. It supplies FE, GP, WOCPU, and SGMII TX/RX/CDR gates.

## Important APIs, types, and functions

Key data includes `sgmii0_clks[]`, `sgmii1_clks[]`, `eth_clks[]`, and descriptors `eth_desc`, `sgmii0_desc`, and `sgmii1_desc`. The OF match table maps `"mediatek,mt7981-ethsys"`, `"mediatek,mt7981-sgmiisys_0"`, and `"mediatek,mt7981-sgmiisys_1"` to `mtk_clk_simple_probe()`.

## Control flow, state, and persistence

Generic probe registers the descriptor selected by compatible string. Eth gates use inverted no-setclr operations at offset `0x30`; SGMII gates use offset `0xe4`. State is hardware gate bits and CCF provider registration.

## Dependencies and integration points

Dependencies include `clk-mtk.h`, `clk-gate.h`, and `dt-bindings/clock/mediatek,mt7981-clk.h`. Parent clocks are topckgen outputs like `netsys_2x`, `sgm_325m`, `netsys_wed_mcu`, `usb_tx250m`, `usb_eq_rx250m`, `usb_ln0`, and `usb_cdr`. Consumers include MediaTek Ethernet, SGMII PHY glue, and WED offload firmware/CPU paths.

## Risks and test signals

Risks include parent-name drift between topckgen and ethsys, inverted gate polarity mistakes, and WOCPU clock dependency failures. Test Ethernet traffic, SGMII0/1 links, WED offload, and clock summary gates.
