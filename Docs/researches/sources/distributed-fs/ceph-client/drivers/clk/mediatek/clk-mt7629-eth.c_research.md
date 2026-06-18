# sources/distributed-fs/ceph-client/drivers/clk/mediatek/clk-mt7629-eth.c

## Purpose

This MT7629 Ethernet driver registers ethsys and two SGMII system clock providers. It also registers an ethsys reset controller.

## Important APIs, types, and functions

Important definitions are `eth_clks[]`, a two-dimensional `sgmii_clks[2][4]`, `clk_mt7629_ethsys_init()`, `clk_mt7629_sgmiisys_init()`, `clk_mt7629_eth_probe()`, and `clk_rst_desc`. The platform driver is built in with `builtin_platform_driver()`.

## Control flow, state, and persistence

Probe dispatches to a match-data init function. Ethsys allocates `CLK_ETH_NR_CLK`, registers inverted no-setclr gates, publishes the provider, and registers reset bank `0x34`. Sgmiisys allocates `CLK_SGMII_NR_CLK` and uses a static `id` to pick the first or second SGMII gate array before publishing the provider. State includes the static SGMII instance counter, hardware gates, reset provider, and CCF provider registrations.

## Dependencies and integration points

Dependencies are MT7629 bindings and MediaTek gate/reset helpers. Parents include `eth2pll`, `txclk_src_pre`, `eth_500m`, and USB-derived SGMII reference clocks. Consumers are Ethernet FE/GMAC, switch, and two SGMII PHY instances.

## Risks and test signals

The static `id++` makes SGMII assignment depend on probe order and has no bound check. Other risks are inverted gate polarity and ignoring reset registration errors. Test both SGMII instances in either DT order, Ethernet traffic, reset users, and built-in early boot.
